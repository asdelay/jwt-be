from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from app.models import Role

# Single source of truth for emails: validated, max 50 chars (matches the users.email column),
# and fully lowercased so every write and lookup agrees on one canonical form.
Email = Annotated[EmailStr, Field(max_length=50), AfterValidator(str.lower)]

class SUserAdd(BaseModel):
    email: Email
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
    email: Email

class SRegister(BaseModel):
    # role is deliberately absent: clients must never choose their own role
    email: Email

class SVerifyCode(BaseModel):
    code: str
    email: Email