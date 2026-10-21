app with full jwt rotation

TODO: 

    add pydantic schema validation (for email espcly)

1. run the db with `docker compose up`

hints for myself =) 

run migration - `alembic revision --autogenerate -m "comment"`

apply migration - `alembic upgrade head`

rollback migration - `alembic downgrade head`