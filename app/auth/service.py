import hmac
import smtplib
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage

import aiosmtplib

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constants import OTP_EXPIRATION_MINUTES, MAX_OTP_VERIFICATION_ATTEMPTS
from app.credentials import settings
from app.exceptions import NotFoundError, UnauthorizedError
from app.models import User, Otp
from app.schemas import SLogin
from app.utils import generate_otp, hash_otp, create_access_token


async def login_by_email(login_data: SLogin, session: AsyncSession):
    query = select(User).where(User.email == login_data.email).options(selectinload(User.flowers))

    user = (await session.execute(query)).scalar_one_or_none()

    if user is None:
        raise NotFoundError("Failed to log in")

    code = generate_otp()

    saved_otp = await save_otp(code, user, session)

    email_sent = await send_verification_email(user.email, code)

    # send code by email
    # verify code
    # if code is valid, generate jwt and send it to user

    return email_sent

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

async def verify_code_by_id(code: str, user_id: int, session: AsyncSession) -> str:
    now = datetime.now(timezone.utc)

    otp = (
        await session.execute(
            select(Otp)
            .where(
                Otp.user_id == user_id,
                Otp.used_at.is_(None),
                Otp.expires_at > now,
            )
            .options(selectinload(Otp.user))
            .order_by(Otp.created_at.desc())
            .limit(1)
            .with_for_update()
        )
    ).scalar_one_or_none()

    if otp is None or otp.attempts >= MAX_OTP_VERIFICATION_ATTEMPTS:
        raise UnauthorizedError("Failed to Log in")

    if not hmac.compare_digest(otp.code_hash, hash_otp(user_id, code)):
        otp.attempts += 1
        await session.commit()
        raise UnauthorizedError("Failed to Log in")

    otp.used_at = now
    await session.commit()

    access_token = create_access_token(otp.user)
    return access_token

