from fastapi import APIRouter, Response, BackgroundTasks, Depends

from app.credentials import settings
from app.types import SessionDep
from app.schemas import SLogin, SVerifyCode
from app.utils import ACCESS_TTL
from app.auth.service import login_by_email, verify_code_by_email, get_current_user
from app.models import User

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return user

@auth_router.post("/login")
async def login(login_data: SLogin, session: SessionDep, background_tasks: BackgroundTasks):
    return await login_by_email(background_tasks, login_data, session)

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
    access_token = await verify_code_by_email(code.code, code.email, session)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,  # True in prod, False on localhost
        samesite="lax",
        max_age=int(ACCESS_TTL.total_seconds()),
        path="/"
    )

    return {"access_token": access_token}

