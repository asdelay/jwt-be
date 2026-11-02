import hmac
from datetime import timedelta, datetime, timezone
from email.message import EmailMessage

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import aiosmtplib

from app.schemas import SUserAdd, SFlowerAdd, SFlowerUpdate, SLogin

from app.models import User, Flower, Otp
from app.exceptions import AlreadyExistsError, NotFoundError, BadRequestError, UnauthorizedError
from app.utils import generate_otp, hash_otp, create_access_token
from app.credentials import settings
from app.constants import MAX_OTP_VERIFICATION_ATTEMPTS, OTP_EXPIRATION_MINUTES


async def add_user(user: SUserAdd, session: AsyncSession) -> User:
    new_user = User(**user.model_dump(), flowers=[])
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise AlreadyExistsError(message="User with such email already exists")

    return new_user

async def fetch_all_users(session: AsyncSession):
    # selectinload bc pydantic will try to serialize User.flowers but no User.flowers is available
    # bc in async sqlalchemy lazy loading (default loading) doesn't rly work
    query = select(User).options(selectinload(User.flowers))
    result = await session.scalars(query)
    return result.all()

async def delete_user_by_id(id: int, session: AsyncSession):
    query = select(User).where(User.id == id)
    result = await session.execute(query)
    user = result.scalars().one_or_none()

    if(user is None):
        raise NotFoundError(message="This user does not exist")

    await session.delete(user)
    await session.commit()

    return {"response": f"User {user.id} is deleted"}

async def add_flower(flower:SFlowerAdd, session: AsyncSession):
    creator_id_from_client = flower.creator_id

    query = select(User).where(User.id == creator_id_from_client)
    result = await session.execute(query)
    user = result.scalars().one_or_none()

    if user is None:
        raise NotFoundError("This user does not exist")

    new_flower = Flower(**flower.model_dump(), creator=user)
    session.add(new_flower)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise BadRequestError("Failed to create flower")

    return new_flower

async def fetch_all_flowers(session: AsyncSession):
    query = select(Flower).options(selectinload(Flower.creator))
    result = await session.scalars(query)
    return result.all()

async def update_flower_by_id(id: int, updated_flower: SFlowerUpdate, session: AsyncSession):
    flower = await session.get(Flower, id)

    if flower is None:
        raise NotFoundError("Flower with such id does not exist")

    update_data = updated_flower.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(flower, field, value)

    await session.commit()
    return flower

async def delete_flower_by_id(id: int, session: AsyncSession):
    flower = await session.get(Flower, id)

    if flower is None:
        raise NotFoundError("Flower with such id does not exist")

    await session.delete(flower)
    await session.commit()
    return flower

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

