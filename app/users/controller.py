from fastapi import APIRouter

from app.schemas import SUserAdd, SUser, SUserUpdate
from app.types import SessionDep
from app.users.service import add_user, fetch_all_users, delete_user_by_id, update_user_by_id
from app.auth.service import AdminDep, CurrentUserDep

# RBAC is applied per route (not on the router), because DELETE is open to regular users for their own account
users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("", response_model=SUser)
async def create_user(user: SUserAdd, session: SessionDep, _admin: AdminDep):
    # admin only: regular sign-up goes through /auth/register, which can't set a role
    return await add_user(user, session)

@users_router.get("", response_model=list[SUser])
async def get_all_users(session: SessionDep, _admin: AdminDep):
    # admin only: users see themselves via /auth/me
    return await fetch_all_users(session)

@users_router.patch("/{id}", response_model=SUser)
async def update_user(id: int, data: SUserUpdate, session: SessionDep, current_user: CurrentUserDep):
    # username: only the account owner; role: only admins, and not on themselves
    return await update_user_by_id(id, data, session, current_user)

@users_router.delete("/{id}")
async def delete_user(id: int, session: SessionDep, current_user: CurrentUserDep):
    # any logged-in user may delete their own account; admins may delete anyone
    return await delete_user_by_id(id, session, current_user)
