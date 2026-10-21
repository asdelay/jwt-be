from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.credentials import settings

engine = create_async_engine(settings.get_connection_string())

session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with session_maker() as session:
        yield session