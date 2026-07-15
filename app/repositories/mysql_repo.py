from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql_models import (
    Candidate,
    Job,
    CandidateSkill,
    CandidateSkillList,
    JobRequiredSkill,
    Education,
    WorkExperience,
)


class MySQLRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------
    # JOBS
    # ------------------------------------------------------------------

    async def get_active_jobs(self, limit: int = 100) -> list[Job]:
        stmt = (
            select(Job)
            .where(Job.job_status == True)  # noqa: E712 (bit(1) -> bool, explicit compare is clearer here)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())



    async def get_job_by_id(self, job_id: int) -> Job | None:
        stmt = select(Job).where(Job.job_id == job_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_job_required_skills(self, job_id: int) -> list[str]:
        stmt = select(JobRequiredSkill.skill).where(JobRequiredSkill.job_id == job_id)
        result = await self.session.execute(stmt)
        return [s for s in result.scalars().all() if s]

    # ------------------------------------------------------------------
    # CANDIDATES
    # ------------------------------------------------------------------

    async def get_candidate_by_id(self, candidate_id: int) -> Candidate | None:
        stmt = select(Candidate).where(Candidate.candidate_id == candidate_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()


    async def get_active_candidates(self, limit: int = 100) -> list[Candidate]:
        stmt = (
            select(Candidate)
            .where(Candidate.active_status == True)  # noqa: E712
            .order_by(Candidate.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def get_candidate_skills(self, candidate_id: int) -> list[CandidateSkill]:
       
        stmt = select(CandidateSkill).where(CandidateSkill.candidate_id == candidate_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_candidate_skill_list(self, candidate_id: int) -> list[str]:
        stmt = select(CandidateSkillList.skill_list).where(
            CandidateSkillList.candidate_candidate_id == candidate_id
        )
        result = await self.session.execute(stmt)
        return [s for s in result.scalars().all() if s]

    async def get_candidate_education(self, candidate_id: int) -> list[Education]:
        stmt = select(Education).where(Education.candidate_id == candidate_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_candidate_work_experience(self, candidate_id: int) -> list[WorkExperience]:
        stmt = select(WorkExperience).where(WorkExperience.candidate_id == candidate_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # AGGREGATED FETCH — full candidate profile for scoring
    # ------------------------------------------------------------------

    async def get_candidate_full_profile(self, candidate_id: int) -> dict | None:
       
        candidate = await self.get_candidate_by_id(candidate_id)
        if candidate is None:
            return None

        skills = await self.get_candidate_skills(candidate_id)
        skill_list = await self.get_candidate_skill_list(candidate_id)
        education = await self.get_candidate_education(candidate_id)
        work_experience = await self.get_candidate_work_experience(candidate_id)

        return {
            "candidate": candidate,
            "skills": skills,               # list[CandidateSkill] — has experience/rating
            "skill_list": skill_list,        # list[str] — fallback flat tags
            "education": education,
            "work_experience": work_experience,
        }

    async def get_job_full_profile(self, job_id: int) -> dict | None:
        job = await self.get_job_by_id(job_id)
        if job is None:
            return None

        required_skills = await self.get_job_required_skills(job_id)

        return {
            "job": job,
            "required_skills": required_skills,
        }