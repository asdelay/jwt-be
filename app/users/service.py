from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas import SUserAdd, SUserUpdate
from app.auth.service import CurrentUser
from app.models import User, Role
from app.exceptions import AlreadyExistsError, NotFoundError, ForbiddenError, BadRequestError


async def add_user(user: SUserAdd, session: AsyncSession) -> User:
    new_user = User(**user.model_dump(), flowers=[])
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise AlreadyExistsError(message="User with such email or username already exists")

    return new_user

async def fetch_all_users(session: AsyncSession):
    # selectinload bc pydantic will try to serialize User.flowers but no User.flowers is available
    # bc in async sqlalchemy lazy loading (default loading) doesn't rly work
    query = select(User).options(selectinload(User.flowers))
    result = await session.scalars(query)
    return result.all()

async def _get_user_or_404(id: int, session: AsyncSession, *options) -> User:
    """Shared lookup; *options lets callers add loaders, e.g. selectinload(User.flowers)."""
    user = (await session.execute(select(User).where(User.id == id).options(*options))).scalar_one_or_none()
    if user is None:
        raise NotFoundError(message="This user does not exist")
    return user


async def _ensure_not_last_admin(user: User, session: AsyncSession):
    """Call before demoting or deleting `user`. Raises if they're the only admin left.

    SELECT ... FOR UPDATE locks every admin row until this transaction commits. If two admins demote
    each other at the same time, the second request waits on the lock, then re-reads and sees only
    one admin left -> refused. Without the lock both would count 2 admins and both would succeed.
    """
    if user.role != Role.admin:
        return
    admin_ids = (await session.execute(
        select(User.id).where(User.role == Role.admin).with_for_update()
    )).scalars().all()
    if len(admin_ids) <= 1:
        raise ForbiddenError("Can't remove the last admin")


async def delete_user_by_id(id: int, session: AsyncSession, current_user: CurrentUser):
    # permission check first: otherwise 404 vs 403 would tell a regular user which user ids exist
    # allow-list (owner or admin) rather than deny-list (role == user), so any future role is denied by default
    if id != current_user.id and current_user.role != Role.admin:
        raise ForbiddenError("You can only delete your own account")

    user = await _get_user_or_404(id, session)
    await _ensure_not_last_admin(user, session)  # deleting an admin also removes an admin

    await session.delete(user)
    await session.commit()

    return {"response": f"User {user.id} is deleted"}


async def update_user_by_id(id: int, data: SUserUpdate, session: AsyncSession, current_user: CurrentUser) -> User:
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise BadRequestError("Nothing to update")

    if "username" in changes and id != current_user.id:
        raise ForbiddenError("You can only change your own username")
    if "role" in changes:
        if current_user.role != Role.admin:
            raise ForbiddenError("Only admins can change roles")
        if id == current_user.id:
            raise ForbiddenError("Admins can't change their own role")

    user = await _get_user_or_404(id, session, selectinload(User.flowers))

    if "role" in changes and changes["role"] != Role.admin:
        await _ensure_not_last_admin(user, session)

    for field, value in changes.items():
        setattr(user, field, value)  # updated_at is bumped by onupdate=func.now() on the model

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        if "username" in changes:
            raise AlreadyExistsError(message="This username is already taken")
        raise

    return user
