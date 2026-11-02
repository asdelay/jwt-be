app with full jwt rotation

TODO: 

    protect routes that need to be protected w authentication
    send verification email as a background task
    organize better folder structure
    add rate limiting (especially on auth routes)



    later add redis (otps, tokens, popular flowers)
    clear dbs from old expired otps

1. run the db with `docker compose up`

hints for myself =) 

run migration - `alembic revision --autogenerate -m "comment"`

apply migration - `alembic upgrade head`

rollback migration - `alembic downgrade head`