from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.models import Role

# Single source of truth for emails: validated, max 50 chars (matches the users.email column),
# and fully lowercased so every write and lookup agrees on one canonical form.
Email = Annotated[EmailStr, Field(max_length=50), AfterValidator(str.lower)]
# trimmed + lowercased so 'Alice' and 'alice' can't be two different accounts; max 50 matches users.username
Username = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=1, max_length=50)]

class SUserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Role
    username: Username

class SUserAdd(BaseModel):
    email: Email
    username: Username
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
    creator: SUserBrief

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