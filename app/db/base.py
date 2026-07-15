
from sqlalchemy.orm import DeclarativeBase


class MySQLBase(DeclarativeBase):
    """Base class for read-only MySQL ORM models."""
    pass


class PostgresBase(DeclarativeBase):
    """Base class for read/write PostgreSQL ORM models."""
    pass