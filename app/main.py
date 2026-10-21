from fastapi import FastAPI

from app.controller import router

app = FastAPI()

@app.get("/")
async def base():
    return {"status": "ok"}

app.include_router(router)