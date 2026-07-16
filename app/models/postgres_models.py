from datetime import datetime

from sqlalchemy import String, Text, Float, Integer, DateTime, JSON, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import PostgresBase


class CandidateScore(PostgresBase):
    __tablename__ = "candidate_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(BigInteger, index=True)
    job_id: Mapped[int] = mapped_column(BigInteger, index=True)

    # (rule-based) scores
    skills_score: Mapped[float] = mapped_column(Float)
    tech_score: Mapped[float] = mapped_column(Float)
    experience_score: Mapped[float] = mapped_column(Float)
    education_score: Mapped[float] = mapped_column(Float)

    # (LLM) scores
    project_relevance_score: Mapped[float] = mapped_column(Float)
    contextual_fit_score: Mapped[float] = mapped_column(Float)
    llm_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Combined
    final_score: Mapped[float] = mapped_column(Float, index=True)

    # Structured breakdown for debugging (matched/missing skills, ranges, etc.)
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    scored_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<CandidateScore candidate={self.candidate_id} job={self.job_id} score={self.final_score}>"


class JobRecommendation(PostgresBase):
    __tablename__ = "job_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, index=True)
    candidate_id: Mapped[int] = mapped_column(BigInteger)
    rank: Mapped[int] = mapped_column(Integer)
    final_score: Mapped[float] = mapped_column(Float)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<JobRecommendation job={self.job_id} candidate={self.candidate_id} rank={self.rank}>"


class ProcessedTracker(PostgresBase):
   
    __tablename__ = "processed_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(BigInteger, index=True)
    job_id: Mapped[int] = mapped_column(BigInteger, index=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<ProcessedTracker candidate={self.candidate_id} job={self.job_id}>"


class ScoringLog(PostgresBase):
    __tablename__ = "scoring_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_started_at: Mapped[datetime] = mapped_column(DateTime)
    run_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    jobs_processed: Mapped[int] = mapped_column(Integer, default=0)
    candidates_scored: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="running")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ScoringLog id={self.id} status={self.status}>"