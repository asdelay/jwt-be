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
    is_public: bool = False
    creator_id: int

class SFlower(SFlowerAdd):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creator: SUserAdd

class SFlowerUpdate(BaseModel):
    name: str | None = None
    is_public: bool = False