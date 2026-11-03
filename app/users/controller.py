from fastapi import APIRouter

from app.schemas import SUserAdd, SUser
from app.types import SessionDep
from app.users.service import add_user, fetch_all_users, delete_user_by_id

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("", response_model=SUser)
async def create_user(user: SUserAdd, session: SessionDep):
    return await add_user(user, session)

@users_router.get("", response_model=list[SUser])
async def get_all_users(session: SessionDep) -> list [SUser]:
    return await fetch_all_users(session)

@users_router.delete("/{id}")
async def delete_user(id: int, session: SessionDep):
    return await delete_user_by_id(id, session)