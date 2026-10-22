from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SUserAdd, SUser, SFlowerAdd, SFlower
from app.service import add_user, fetch_all_users, delete_user_by_id, add_flower, fetch_all_flowers
from app.db import get_session

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("/users")
async def create_user(user: Annotated[SUserAdd, Depends()], session: SessionDep):
    return await add_user(user, session)

@router.get("/users", response_model=list[SUser])
async def get_all_users(session: SessionDep) -> list [SUser]:
    return await fetch_all_users(session)

@router.delete("/users/{id}")
async def delete_user(id: int, session: SessionDep):
    return await delete_user_by_id(id, session)


@router.post("/flowers")
async def create_flower(flower: Annotated[SFlowerAdd, Depends()], session: SessionDep):
    return await add_flower(flower, session)

@router.get("/flowers", response_model=list[SFlower])
async def get_all_flowers(session: SessionDep) -> list [SFlower]:
    return await fetch_all_flowers(session)