from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.mysql import get_mysql_db
from app.db.postgres import get_postgres_db

app = FastAPI(title="Resume Scoring Engine")


@app.get("/health/mysql")
async def health_mysql(db: AsyncSession = Depends(get_mysql_db)):
    result = await db.execute(text("SELECT 1"))
    return {"mysql": "connected", "result": result.scalar()}


@app.get("/health/postgres")
async def health_postgres(db: AsyncSession = Depends(get_postgres_db)):
    result = await db.execute(text("SELECT 1"))
    return {"postgres": "connected", "result": result.scalar()}