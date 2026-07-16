from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres_models import CandidateScore, JobRecommendation, ProcessedTracker, ScoringLog

class PostgresRepository:
    def __init__(self, session:AsyncSession):
        self.session = session
        
    # Candidate Scores
    
    async def save_candidate_score(self, score_data: dict)->CandidateScore:
        record = CandidateScore(**score_data)
        self.session.add(record)
        await self.session.flush()
        return record


    async def get_scores_for_job(self, job_id:int)-> list[CandidateScore]:
        stmt = (
            select(CandidateScore)
            .where(CandidateScore.job_id == job_id)
            .order_by(CandidateScore.final_score.desc())
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

# Processed Tracker

    async def is_already_processed(self, candidate_id: int, job_id: int)-> bool:
        stmt = select(ProcessedTracker).where(
            ProcessedTracker.candidate_id==candidate_id,
            ProcessedTracker.job_id == job_id,
        )
        result = await self.session.execute(stmt)
        
        return result.scalars().first() is not None
    
    async def mark_processed(self,candidate_id: int, job_id: int)-> None:
        record = ProcessedTracker(candidate_id = candidate_id, job_id = job_id)
        self.session.add(record)
        await self.session.flush()
        
    # Top 5 Recommendations
    
    async def cache_top5_recommendations(self, job_id: int, ranked_candidates: list[dict]) -> None:
        # clear old cache for this job first 
        
        for rank, entry in enumerate(ranked_candidates[:5],start=1):
            record = JobRecommendation(
                job_id = job_id,
                candidate_id = entry["candidate_id"],
                rank = rank,
                final_score = entry["final_score"],
            )
            self.session.add(record)
        await self.session.flush()
        
        
    async def get_top5_for_job(self, job_id: int)-> list[JobRecommendation]:
        stmt = (
            select(JobRecommendation).where (JobRecommendation.job_id == job_id)
            .order_by(JobRecommendation.rank.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    # Scoring Logs
    
    async def start_scoring_log(self)-> ScoringLog:
        log = ScoringLog(run_started_at = datetime.utcnow(),status="running")
        self.session.add(log)
        await self.session.flush()
        return log
    
    async def complete_scoring_log(
        self, log_id: int, jobs_processed: int, candidates_scored: int, status: str, error_message: str | None = None) -> None:
        
        stmt = select(ScoringLog).where(ScoringLog.id == log_id)
        result = await self.session.execute(stmt)
        log = result.scalars().first()
        if log:
            log.run_completed_at = datetime.utcnow()
            log.jobs_processed = jobs_processed
            log.candidates_scored = candidates_scored
            log.status =  status
            log.error_message = error_message
            await self.session.flush()
            

