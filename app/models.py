import enum

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Role(enum.Enum):
    admin = "Admin"
    user = "User"

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[Role]

class Flower(Base):


class RefreshToken(Base):
