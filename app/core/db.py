from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session