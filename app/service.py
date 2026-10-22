from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas import SUserAdd, SUser

from app.models import User
from app.exceptions import AlreadyExistsError, NotFoundError


async def add_user(user: SUserAdd, session: AsyncSession) -> SUserAdd:
    new_user = User(**user.model_dump())
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise AlreadyExistsError(message="User with such email already exists")

    return user

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