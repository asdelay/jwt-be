import asyncio

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://postgres:12345678@localhost:5432/jwt_db")
# async def main():
#     engine = create_async_engine("postgresql+asyncpg://postgres:12345678@localhost:5432/jwt_db")
#     session = AsyncSession(engine, expire_on_commit=False)
#
#     res = await session.execute(text("select 'hello world'"))
#     result = res.scalars().first()
#     print(result)
#
#     await engine.dispose()
#
# asyncio.run(main())