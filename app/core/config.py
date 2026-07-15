from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- App ----------
    app_name: str = "Resume Scoring Engine"
    app_env: str = "development"
    log_level: str = "INFO"

    # ---------- MySQL (Read-Only) ----------
    mysql_url: str
    mysql_pool_size: int = 5
    mysql_max_overflow: int = 10

    # ---------- PostgreSQL (Read/Write) ----------
    postgres_url: str
    postgres_pool_size: int = 5
    postgres_max_overflow: int = 10

    # ---------- Groq / LangChain ----------
    groq_api_key: str
    groq_model: str = "llama3-8b-8192"

    # ---------- Scheduler ----------
    scheduler_enabled: bool = True
    scheduler_interval_minutes: int = 30

    # ---------- Scoring Weights ----------
    weight_skills: float = 0.25
    weight_tech: float = 0.20
    weight_experience: float = 0.15
    weight_education: float = 0.05
    weight_project_relevance: float = 0.20
    weight_contextual_fit: float = 0.15

    @field_validator("mysql_url")
    @classmethod
    def validate_mysql_driver(cls, v: str) -> str:
        """Guard against accidentally using the sync mysqlclient/pymysql driver."""
        if not v.startswith("mysql+aiomysql://"):
            raise ValueError(
                "MYSQL_URL must use the async driver: mysql+aiomysql://..."
            )
        return v

    @field_validator("postgres_url")
    @classmethod
    def validate_postgres_driver(cls, v: str) -> str:
        """Guard against accidentally using the sync psycopg2 driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "POSTGRES_URL must use the async driver: postgresql+asyncpg://..."
            )
        return v

    @property
    def total_weight(self) -> float:
        """Sanity-check helper: all scoring weights should sum to 1.0."""
        return round(
            self.weight_skills
            + self.weight_tech
            + self.weight_experience
            + self.weight_education
            + self.weight_project_relevance
            + self.weight_contextual_fit,
            4,
        )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. Ensures the .env file is parsed only once
    per process and the same Settings instance is reused everywhere
    (import this function, not Settings directly).
    """
    return Settings()