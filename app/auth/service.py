import hmac
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
from typing import Annotated

import aiosmtplib
import jwt
from fastapi import BackgroundTasks
from fastapi.params import Depends
from fastapi.security import APIKeyCookie

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constants import OTP_EXPIRATION_MINUTES, MAX_OTP_VERIFICATION_ATTEMPTS
from app.credentials import settings
from app.exceptions import AppError, UnauthorizedError, ForbiddenError
from app.models import User, Otp, Role
from app.schemas import SLogin, SRegister
from app.utils import generate_otp, hash_otp, create_access_token

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

def _normalize_email(email: str) -> str:
    return email.strip().lower()


async def _get_user_by_email(email: str, session: AsyncSession) -> User | None:
    return (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()


async def register_by_email(background_tasks: BackgroundTasks, data: SRegister, session: AsyncSession):
    email = _normalize_email(data.email)
    user = await _get_user_by_email(email, session)

    if user is None:
        session.add(User(email=email, role=Role.user))
        try:
            await session.commit()
        except IntegrityError:
            # a concurrent request registered the same email first - the unique constraint is the real guard
            await session.rollback()
        user = await _get_user_by_email(email, session)
        if user is None:
            raise AppError()

    # existing or new user: same OTP flow and same response, so registration can't be used to probe emails
    code = generate_otp()
    await save_otp(code, user, session)
    background_tasks.add_task(send_verification_email, user.email, code)

    return {"message": f"Verification code was sent to {email}"}


async def login_by_email(background_tasks: BackgroundTasks, login_data: SLogin, session: AsyncSession):
    email = _normalize_email(login_data.email)
    user = await _get_user_by_email(email, session)

    if user is not None:
        code = generate_otp()
        await save_otp(code, user, session)
        background_tasks.add_task(send_verification_email, user.email, code)

    return {"message": f"Verification code was sent to {email}"}

async def save_otp(code: str, user: User, session: AsyncSession):
    now = datetime.now(timezone.utc)
    otp_ttl = timedelta(minutes=OTP_EXPIRATION_MINUTES)

    # invalidating user's prev sessions
    await session.execute(
        update(Otp)
        .where(Otp.user_id == user.id, Otp.used_at.is_(None))
        .values(used_at=now)
    )

    session.add(Otp(user=user, user_id=user.id, code_hash=hash_otp(user.id, code), expires_at=now+otp_ttl))
    await session.commit()
    return code

async def send_verification_email(to_email: str, code: str):
    msg = EmailMessage()
    msg["Subject"] = "Verification Code"
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
    msg.set_content(f"Your verification code: {code}. It expires in {OTP_EXPIRATION_MINUTES} minutes.")

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_user,
        password=settings.smtp_password,
    )

    return {"message": "email sent"}

async def verify_code_by_email(code: str, email: str, session: AsyncSession) -> str:
    now = datetime.now(timezone.utc)
    email = _normalize_email(email)

    otp = (
        await session.execute(
            select(Otp)
            .join(User, Otp.user_id == User.id)
            .where(
                User.email == email,
                Otp.used_at.is_(None),
                Otp.expires_at > now,
            )
            .options(selectinload(Otp.user))
            .order_by(Otp.created_at.desc())
            .limit(1)
            .with_for_update(of=Otp)
        )
    ).scalar_one_or_none()

    if otp is None or otp.attempts >= MAX_OTP_VERIFICATION_ATTEMPTS:
        raise UnauthorizedError()

    if not hmac.compare_digest(otp.code_hash, hash_otp(otp.user_id, code)):
        otp.attempts += 1
        await session.commit()
        raise UnauthorizedError()

    otp.used_at = now
    await session.commit()

    return create_access_token(otp.user)

@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: Role


def _decode_token(token: str) -> CurrentUser:
    try:
        payload = jwt.decode(token, settings.access_token_secret, algorithms=['HS256'], options={"require": ["exp", "sub"]})
        # Role(...) raises ValueError for an unknown role string -> treated as an invalid token
        return CurrentUser(id=int(payload["sub"]), role=Role(payload["role"]))
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise UnauthorizedError()


async def get_current_user(token: Annotated[str | None, Depends(cookie_scheme)]) -> CurrentUser:
    """Authentication required: 401 if there is no valid token."""
    if token is None:
        raise UnauthorizedError("Not authenticated")
    return _decode_token(token)


async def get_optional_user(token: Annotated[str | None, Depends(cookie_scheme)]) -> CurrentUser | None:
    """Authentication optional: None for anonymous visitors, but a bad/expired token is still a 401."""
    if token is None:
        return None
    return _decode_token(token)


def require_role(*roles: Role):
    """Dependency factory: require_role(Role.admin) returns a dependency that only lets those roles through."""
    async def checker(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if user.role not in roles:
            raise ForbiddenError("You don't have permission to perform this action")
        return user
    return checker


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
OptionalUserDep = Annotated[CurrentUser | None, Depends(get_optional_user)]
AdminDep = Annotated[CurrentUser, Depends(require_role(Role.admin))]
