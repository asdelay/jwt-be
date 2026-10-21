from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import Role

class SUserAdd(BaseModel):
    email: EmailStr
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