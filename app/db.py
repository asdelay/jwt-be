from sqlalchemy.ext.asyncio import create_async_engine

from credentials import settings

engine = create_async_engine(f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/{settings.postgres_db}")