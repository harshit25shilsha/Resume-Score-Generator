from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import get_settings
settings = get_settings()

mysql_engine = create_async_engine(
    settings.mysql_url,
    pool_size=settings.mysql_pool_size,
    max_overflow=settings.mysql_max_overflow,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=False,
)

MySQLSessionLocal = async_sessionmaker(
    bind=mysql_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_mysql_db():
    async with MySQLSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()