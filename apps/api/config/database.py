from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
try:
    from config.confi import settings
except ModuleNotFoundError:
    from apps.api.config.confi import settings

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
import os 


raw_db_url = settings.DATABASE_URL or os.getenv("DATABASE_URL")
if raw_db_url:
    url = raw_db_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if "sslmode=require" in url:
        url = url.replace("sslmode=require", "ssl=require")
    if "&channel_binding=require" in url:
        url = url.replace("&channel_binding=require", "")
    elif "?channel_binding=require" in url:
        url = url.replace("?channel_binding=require", "")
    Database_Url = url
else:
    Database_Url = f"postgresql+asyncpg://{settings.db_user}:{settings.password}@{settings.host}:{settings.db_port}/{settings.db_name}"



engine = create_async_engine(Database_Url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session