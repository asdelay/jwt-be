from sqlalchemy import select, or_, Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.service import CurrentUser
from app.exceptions import NotFoundError, BadRequestError, ForbiddenError
from app.models import Flower, Role
from app.schemas import SFlowerAdd, SFlowerUpdate


def _visible_to(query: Select, user: CurrentUser | None) -> Select:
    """Apply the read rules to a query: anonymous -> public, user -> public + own, admin -> all."""
    if user is None:
        return query.where(Flower.is_public.is_(True))
    if user.role == Role.admin:
        return query
    return query.where(or_(Flower.is_public.is_(True), Flower.creator_id == user.id))


async def _get_flower_or_404(id: int, session: AsyncSession) -> Flower:
    query = select(Flower).where(Flower.id == id).options(selectinload(Flower.creator))
    flower = (await session.scalars(query)).one_or_none()
    if flower is None:
        raise NotFoundError("Flower with such id does not exist")
    return flower


async def add_flower(flower: SFlowerAdd, user: CurrentUser, session: AsyncSession):
    new_flower = Flower(**flower.model_dump(), creator_id=user.id)
    session.add(new_flower)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise BadRequestError("Failed to create flower")

    # reload with creator so the response can be serialized (no lazy loading in async)
    return await _get_flower_or_404(new_flower.id, session)


async def fetch_flowers(user: CurrentUser | None, session: AsyncSession):
    query = _visible_to(select(Flower).options(selectinload(Flower.creator)), user)
    result = await session.scalars(query)
    return result.all()


async def fetch_flower_by_id(id: int, user: CurrentUser | None, session: AsyncSession):
    flower = await _get_flower_or_404(id, session)

    is_owner = user is not None and flower.creator_id == user.id
    is_admin = user is not None and user.role == Role.admin
    if not (flower.is_public or is_owner or is_admin):
        raise ForbiddenError("This flower is private. Only its owner or an admin can view it")
    return flower


async def update_flower_by_id(id: int, updated_flower: SFlowerUpdate, user: CurrentUser, session: AsyncSession):
    flower = await _get_flower_or_404(id, session)

    # only the owner can update (admins included: they may only read/delete others' flowers)
    if flower.creator_id != user.id:
        raise ForbiddenError("You can only update your own flowers")

    update_data = updated_flower.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(flower, field, value)

    await session.commit()
    return await _get_flower_or_404(id, session)


async def delete_flower_by_id(id: int, user: CurrentUser, session: AsyncSession):
    flower = await _get_flower_or_404(id, session)

    if flower.creator_id != user.id and user.role != Role.admin:
        raise ForbiddenError("You can only delete your own flowers")

    await session.delete(flower)
    await session.commit()
    return flower
