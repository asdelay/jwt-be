app with full jwt rotation

TODO: 

    add authorization level protection on routes (by roles)
    add registration
    add refresh token w rotation and revokation strategy
    add openid connect via google
    add rate limiting (especially on auth routes)



    later add redis (otps, tokens, popular flowers)
    clear db from old expired otps

1. run the db with `docker compose up`

hints for myself =) 

run migration - `alembic revision --autogenerate -m "comment"`

apply migration - `alembic upgrade head`

rollback migration - `alembic downgrade head`