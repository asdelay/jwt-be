from fastapi import APIRouter, Response

from app.credentials import settings
from app.types import SessionDep
from app.schemas import SLogin, SVerifyCode
from app.utils import ACCESS_TTL
from app.auth.service import login_by_email, verify_code_by_id

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login(login_data: SLogin, session: SessionDep):
    return await login_by_email(login_data, session)

@auth_router.post("/register")
async def register():
    return {"message": "not implemented yet"}

@auth_router.get("/me")
async def me():
    return {"message": "not implemented yet"}

@auth_router.post("/refresh")
async def refresh():
    return {"message": "not implemented yet"}

@auth_router.post("/code/verify")
async def verify_code(code: SVerifyCode, response: Response, session: SessionDep):
    access_token = await verify_code_by_id(code.code, code.user_id, session)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,  # True in prod, False on localhost
        samesite="lax",
        max_age=int(ACCESS_TTL.total_seconds()),
        path="/"
    )

    return {"message": "ok"}

