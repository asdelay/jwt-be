from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controller import router
from app.exceptions import AppError

app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code= exc.status_code,
        content = {"error": {"code": exc.code, "message": exc.message}}
    )

@app.exception_handler(Exception)
async def app_handle_unknown_exceptions(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Internal server error"}}
    )

@app.get("/")
async def base():
    return {"status": "ok"}




app.include_router(router)