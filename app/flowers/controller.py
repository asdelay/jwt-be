from fastapi import APIRouter

from app.types import SessionDep
from app.schemas import SFlower, SFlowerAdd, SFlowerUpdate
from app.flowers.service import (
    add_flower,
    fetch_flowers,
    fetch_flower_by_id,
    update_flower_by_id,
    delete_flower_by_id,
)
from app.auth.service import CurrentUserDep, OptionalUserDep

flowers_router = APIRouter(prefix="/flowers", tags=["flowers"])

@flowers_router.post("", response_model=SFlower)
async def create_flower(flower: SFlowerAdd, session: SessionDep, current_user: CurrentUserDep):
    return await add_flower(flower, current_user, session)

@flowers_router.get("", response_model=list[SFlower])
async def get_flowers(session: SessionDep, current_user: OptionalUserDep):
    return await fetch_flowers(current_user, session)

@flowers_router.get("/{id}", response_model=SFlower)
async def get_flower(id: int, session: SessionDep, current_user: OptionalUserDep):
    return await fetch_flower_by_id(id, current_user, session)

@flowers_router.put("/{id}", response_model=SFlower)
async def update_flower(id: int, updated_flower: SFlowerUpdate, session: SessionDep, current_user: CurrentUserDep):
    return await update_flower_by_id(id, updated_flower, current_user, session)

@flowers_router.delete("/{id}", response_model=SFlower)
async def delete_flower(id: int, session: SessionDep, current_user: CurrentUserDep):
    return await delete_flower_by_id(id, current_user, session)
