app with full jwt rotation

TODO: 

    fix response when creating user (no id)  


    POST /users parameters - Depends should be deleted before prod bc now it makes app accept query params instead of body

    

1. run the db with `docker compose up`

hints for myself =) 

run migration - `alembic revision --autogenerate -m "comment"`

apply migration - `alembic upgrade head`

rollback migration - `alembic downgrade head`