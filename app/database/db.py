from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida")

DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)

AsyncSessionLocal = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session