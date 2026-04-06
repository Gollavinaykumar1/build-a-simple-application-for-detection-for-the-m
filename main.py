from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal
from services import item_service
from routers import items

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    error_message = exc.errors()[0]
    return JSONResponse(status_code=400, content={"error": error_message["msg"]})

@app.get("/")
async def read_root():
    return {"message": "Welcome to the malware detection API"}

app.include_router(items.router)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))