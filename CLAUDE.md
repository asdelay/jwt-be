This project uses Fastapi, SQLAlchemy, PostgreSQL, Asyncpg, Pydantic, alembic.
Run db: `docker compose up`
Run app: `uv run fastapi dev`
Create migration: `uv run alembic revision --autogenerate -m "comment"`
Apply migrations: `uv run alembic upgrade head`
Don't apply or rollback migrations without humans permission
If the db schema was updated `docker compose down -v` can be executed in development only.
All sensitive data like API keys and secrets are stored in `.env` file.

Each route lives in `/app/[entity]/controller.py` - then included in `/app/main.py`
Each service lives in `/app/[entity]/service.py`
Models live in `/app/models.py`
Schemas live in `/app/schemas.py`
Errors handled by raising custom error from `/app/exceptions.py`.

DB session: use `SessionDep` from `/app/types.py`
Protected routes: `Depends(get_current_user)` from `/app/auth/service.py` (JWT is read from a cookie)
Config: pydantic-settings in `/app/credentials.py`; when adding an env var, also add it to `.env.example`
No tests yet.

This is a learning project: when writing code, briefly explain the concepts and patterns used.
