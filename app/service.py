from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas import SUserAdd, SUser

from app.models import User


async def add_user(user: SUserAdd, session: AsyncSession) -> SUserAdd:
    new_user = User(email=user.email, role=user.role)
    session.add(new_user)
    await session.commit()
    return user

async def fetch_all_users(session: AsyncSession):
    # selectinload bc pydantic will try to serialize User.flowers but no User.flowers is available
    # bc in async sqlalchemy lazy loading (default loading) doesn't rly work
    query = select(User).options(selectinload(User.flowers))
    result = await session.scalars(query)
    return result.all()
