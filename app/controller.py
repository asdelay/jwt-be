from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SUserAdd, SUser, SFlowerAdd, SFlower, SFlowerUpdate, SLogin, SVerifyCode
from app.service import add_user, fetch_all_users, delete_user_by_id, add_flower, fetch_all_flowers, \
    update_flower_by_id, delete_flower_by_id, login_by_email, verify_code_by_id
from app.db import get_session
from app.credentials import settings
from app.utils import ACCESS_TTL

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("/users", response_model=SUser)
async def create_user(user: SUserAdd, session: SessionDep):
    return await add_user(user, session)

@router.get("/users", response_model=list[SUser])
async def get_all_users(session: SessionDep) -> list [SUser]:
    return await fetch_all_users(session)

@router.delete("/users/{id}")
async def delete_user(id: int, session: SessionDep):
    return await delete_user_by_id(id, session)


@router.post("/flowers", response_model=SFlower)
async def create_flower(flower: SFlowerAdd, session: SessionDep):
    return await add_flower(flower, session)

@router.get("/flowers", response_model=list[SFlower])
async def get_all_flowers(session: SessionDep) -> list [SFlower]:
    return await fetch_all_flowers(session)

@router.put("/flowers/{id}")
async def update_flower(id: int, updated_flower: SFlowerUpdate, session: SessionDep):
    return await update_flower_by_id(id, updated_flower, session)

@router.delete("/flowers/{id}")
async def delete_flower(id: int, session: SessionDep):
    return await delete_flower_by_id(id, session)

@router.post("/auth/login")
async def login(login_data: SLogin, session: SessionDep):
    return await login_by_email(login_data, session)

@router.post("/auth/register")
async def register():
    ...

@router.get("/auth/me")
async def me():
    ...

@router.post("/auth/refresh")
async def refresh():
    ...

@router.post("/auth/code/verify")
async def verify_code(code: SVerifyCode, response: Response, session: SessionDep):
    access_token = await verify_code_by_id(code.code, code.user_id, session)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,  # True in prod, False on localhost
        samesite="lax",
        max_age=int(ACCESS_TTL.total_seconds()),
        path="/"
    )

    return {"message": "ok"}


