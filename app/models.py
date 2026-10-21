import enum

from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Role(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)

    flowers: Mapped[list["Flower"]] = relationship(back_populates="creator")

class Flower(Base):
    __tablename__ = "flowers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    creator: Mapped["User"] = relationship(back_populates="flowers")
