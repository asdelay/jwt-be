from datetime import datetime
import enum

from sqlalchemy import String, ForeignKey, Enum, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import expression


class Base(DeclarativeBase):
    pass

class Role(enum.Enum):
    admin = "admin"
    user = "user"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __mapper_args__ = {"eager_defaults": True}

class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)

    flowers: Mapped[list["Flower"]] = relationship(back_populates="creator", cascade="all, delete-orphan", passive_deletes=True)
    codes: Mapped[list["Otp"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class Flower(TimestampMixin, Base):
    __tablename__ = "flowers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_public: Mapped[bool] = mapped_column(Boolean(False), server_default=expression.false())

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    creator: Mapped["User"] = relationship(back_populates="flowers")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class Otp(TimestampMixin, Base):
    __tablename__ = "otps"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(64), index=True)
    attempts: Mapped[int] = mapped_column(default=0)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user: Mapped["User"] = relationship(back_populates="codes")