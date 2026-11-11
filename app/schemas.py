from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import Role

class SUserAdd(BaseModel):
    email: EmailStr
    role: Role

class SFlowerAdd(BaseModel):
    # client input only: creator comes from the JWT, never from the request body
    name: str
    is_public: bool = False

class SFlowerBrief(SFlowerAdd):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creator_id: int

class SFlower(SFlowerBrief):
    creator: SUserAdd

class SUser(SUserAdd):
    model_config = ConfigDict(from_attributes=True)

    id: int
    flowers: list[SFlowerBrief]

class SFlowerUpdate(BaseModel):
    name: str | None = None
    is_public: bool = False

class SLogin(BaseModel):
    email: str

class SVerifyCode(BaseModel):
    code: str
    email: EmailStr