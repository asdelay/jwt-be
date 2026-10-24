from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas import SUserAdd, SFlowerAdd, SFlowerUpdate

from app.models import User, Flower
from app.exceptions import AlreadyExistsError, NotFoundError, BadRequestError


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

async def delete_user_by_id(id: int, session: AsyncSession):
    query = select(User).where(User.id == id)
    result = await session.execute(query)
    user = result.scalars().one_or_none()

    if(user is None):
        raise NotFoundError(message="This user does not exist")

    await session.delete(user)
    await session.commit()

    return {"response": f"User {user.id} is deleted"}

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

    if(flower is None):
        raise NotFoundError("Flower with such id does not exist")

    update_data = updated_flower.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(flower, field, value)

    await session.commit()
    return flower