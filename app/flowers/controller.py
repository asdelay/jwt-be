from fastapi import APIRouter, Depends

from app.types import SessionDep
from app.schemas import SFlower, SFlowerAdd, SFlowerUpdate
from app.flowers.service import add_flower, fetch_all_flowers, update_flower_by_id, delete_flower_by_id
from app.auth.service import get_current_user
from app.models import User

flowers_router = APIRouter(prefix="/flowers", tags=["flowers"])

@flowers_router.post("", response_model=SFlower)
async def create_flower(flower: SFlowerAdd, session: SessionDep, current_user: User = Depends(get_current_user)):
    return await add_flower(flower, session)

@flowers_router.get("", response_model=list[SFlower])
async def get_all_flowers(session: SessionDep) -> list [SFlower]:
    return await fetch_all_flowers(session)

@flowers_router.put("/{id}")
async def update_flower(id: int, updated_flower: SFlowerUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
    return await update_flower_by_id(id, updated_flower, session)

@flowers_router.delete("/{id}")
async def delete_flower(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    return await delete_flower_by_id(id, session)