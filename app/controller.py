from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SUserAdd, SUser
from app.service import add_user, fetch_all_users
from app.db import get_session

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("/users")
async def create_user(user: Annotated[SUserAdd, Depends()], session: SessionDep):
    return await add_user(user, session)

@router.get("/users", response_model=list[SUser])
async def get_all_users(session: SessionDep) -> list [SUser]:
    return await fetch_all_users(session)