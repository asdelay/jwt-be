from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas import SUserAdd
from app.auth.service import CurrentUser
from app.models import User, Role
from app.exceptions import AlreadyExistsError, NotFoundError, ForbiddenError


async def add_user(user: SUserAdd, session: AsyncSession) -> User:
    new_user = User(**user.model_dump(), flowers=[])
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise AlreadyExistsError(message="User with such email already exists")

    return new_user

async def fetch_all_users(session: AsyncSession):
    # selectinload bc pydantic will try to serialize User.flowers but no User.flowers is available
    # bc in async sqlalchemy lazy loading (default loading) doesn't rly work
    query = select(User).options(selectinload(User.flowers))
    result = await session.scalars(query)
    return result.all()

async def delete_user_by_id(id: int, session: AsyncSession, current_user: CurrentUser):
    # permission check first: otherwise 404 vs 403 would tell a regular user which user ids exist
    # allow-list (owner or admin) rather than deny-list (role == user), so any future role is denied by default
    if id != current_user.id and current_user.role != Role.admin:
        raise ForbiddenError("You can only delete your own account")

    query = select(User).where(User.id == id)
    result = await session.execute(query)
    user = result.scalars().one_or_none()

    if user is None:
        raise NotFoundError(message="This user does not exist")

    await session.delete(user)
    await session.commit()

    return {"response": f"User {user.id} is deleted"}