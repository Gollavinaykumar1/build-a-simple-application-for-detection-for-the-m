# LLM Output

=== FILE: main.py ===
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
=== END ===

=== FILE: models.py ===
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class Item(ItemBase):
    id: int
    class Config:
        orm_mode = True
=== END ===

=== FILE: database.py ===
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
=== END ===

=== FILE: services.py ===
from models import Item
from database import SessionLocal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ItemService:
    async def get_item(self, db: AsyncSession, item_id: int):
        statement = select(ItemModel).where(ItemModel.id == item_id)
        results = await db.execute(statement)
        return results.first()

    async def get_items(self, db: AsyncSession):
        statement = select(ItemModel)
        results = await db.execute(statement)
        return results.all()

    async def create_item(self, db: AsyncSession, item: ItemBase):
        db_item = ItemModel(name=item.name, description=item.description)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def update_item(self, db: AsyncSession, item_id: int, item: ItemBase):
        statement = select(ItemModel).where(ItemModel.id == item_id)
        results = await db.execute(statement)
        db_item = results.first()
        if db_item:
            db_item.name = item.name
            db_item.description = item.description
            await db.commit()
            await db.refresh(db_item)
            return db_item
        return None

    async def delete_item(self, db: AsyncSession, item_id: int):
        statement = select(ItemModel).where(ItemModel.id == item_id)
        results = await db.execute(statement)
        db_item = results.first()
        if db_item:
            await db.delete(db_item)
            await db.commit()
            return True
        return False

item_service = ItemService()
=== END ===

=== FILE: routers/items.py ===
from fastapi import APIRouter, Depends, HTTPException
from models import Item, ItemBase
from services import item_service
from database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter()

@router.get("/items/", response_model=List[Item])
async def read_items(db: AsyncSession = Depends(SessionLocal)):
    items = await item_service.get_items(db)
    return items

@router.post("/items/", response_model=Item)
async def create_item(item: ItemBase, db: AsyncSession = Depends(SessionLocal)):
    return await item_service.create_item(db, item)

@router.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int, db: AsyncSession = Depends(SessionLocal)):
    db_item = await item_service.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemBase, db: AsyncSession = Depends(SessionLocal)):
    db_item = await item_service.update_item(db, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(SessionLocal)):
    if await item_service.delete_item(db, item_id):
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")
=== END ===

=== FILE: requirements.txt ===
fastapi
uvicorn[standard]
sqlalchemy
aiosqlite
asyncpg
pydantic
python-dotenv
=== END ===