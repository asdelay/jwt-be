from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def base():
    return {"status": "ok"}