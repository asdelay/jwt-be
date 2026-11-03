from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import NotFoundError, BadRequestError
from app.models import User, Flower
from app.schemas import SFlowerAdd, SFlowerUpdate


async def add_flower(flower:SFlowerAdd, session: AsyncSession):
    creator_id_from_client = flower.creator_id

    query = select(User).where(User.id == creator_id_from_client)
    result = await session.execute(query)
    user = result.scalars().one_or_none()

    if user is None:
        raise NotFoundError("This user does not exist")

    new_flower = Flower(**flower.model_dump(), creator=user)
    session.add(new_flower)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise BadRequestError("Failed to create flower")

    return new_flower

async def fetch_all_flowers(session: AsyncSession):
    query = select(Flower).options(selectinload(Flower.creator))
    result = await session.scalars(query)
    return result.all()

async def update_flower_by_id(id: int, updated_flower: SFlowerUpdate, session: AsyncSession):
    flower = await session.get(Flower, id)

    if flower is None:
        raise NotFoundError("Flower with such id does not exist")

    update_data = updated_flower.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(flower, field, value)

    await session.commit()
    return flower

async def delete_flower_by_id(id: int, session: AsyncSession):
    flower = await session.get(Flower, id)

    if flower is None:
        raise NotFoundError("Flower with such id does not exist")

    await session.delete(flower)
    await session.commit()
    return flower