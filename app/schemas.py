from pydantic import BaseModel, ConfigDict

from app.models import Role

class SUserAdd(BaseModel):
    email: str
    role: Role

class SUser(SUserAdd):
    model_config = ConfigDict(from_attributes=True)

    id: int
    flowers: list[SFlower]

class SFlowerAdd(BaseModel):
    name: str

class SFlower(SFlowerAdd):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creator_id: int
    creator: SUserAdd