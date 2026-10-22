from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import Role

class SUserAdd(BaseModel):
    email: EmailStr
    role: Role

class SUser(SUserAdd):
    model_config = ConfigDict(from_attributes=True)

    id: int
    flowers: list[SFlowerAdd]

class SFlowerAdd(BaseModel):
    name: str
    creator_id: int

class SFlower(SFlowerAdd):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creator: SUserAdd