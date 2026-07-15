from datetime import datetime

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import MySQLBase


class Candidate(MySQLBase):
    __tablename__ = "candidate"

    candidate_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_designation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currently_working_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    key_experience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    key_experience_in_month: Mapped[str | None] = mapped_column(String(255), nullable=True)
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_file_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active_status: Mapped[bool | None] = mapped_column(nullable=True)
    rating: Mapped[int | None] = mapped_column(nullable=True)
    candidate_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<Candidate id={self.candidate_id} name={self.first_name} {self.last_name}>"


class Job(MySQLBase):
    __tablename__ = "jobs"

    job_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    minimum_experience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    maximum_experience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    minimum_qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preffered_qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    no_of_position: Mapped[int | None] = mapped_column(nullable=True)
    notice_period: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_status: Mapped[bool | None] = mapped_column(nullable=True)
    jobs_posted_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    posted_date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<Job id={self.job_id} title={self.job_title!r}>"



class CandidateSkill(MySQLBase):

    __tablename__ = "candidate_skills"

    candidate_skills_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    candidate_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    skills: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rating: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<CandidateSkill candidate_id={self.candidate_id} skills={self.skills!r}>"



class CandidateSkillList(MySQLBase):
    
    __tablename__ = "candidate_skill_list"

    candidate_candidate_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    skill_list: Mapped[str] = mapped_column(String(255), primary_key=True)

    def __repr__(self) -> str:
        return f"<CandidateSkillList candidate_id={self.candidate_candidate_id} skill={self.skill_list!r}>"


class JobRequiredSkill(MySQLBase):
    
    __tablename__ = "jobs_required_skills"

    job_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    skill: Mapped[str] = mapped_column(String(255), primary_key=True)

    def __repr__(self) -> str:
        return f"<JobRequiredSkill job_id={self.job_id} skill={self.skill!r}>"
    
    
class Education(MySQLBase):
    __tablename__ = "education"

    education_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    candidate_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    degree_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    institution_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    university: Mapped[str | None] = mapped_column(String(255), nullable=True)
    board: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passing_year: Mapped[str | None] = mapped_column(String(255), nullable=True)
    percentage: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Education candidate_id={self.candidate_id} degree={self.degree_name!r}>"


class WorkExperience(MySQLBase):
    __tablename__ = "work_experience"

    work_experience_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    candidate_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_currently_working: Mapped[bool | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<WorkExperience candidate_id={self.candidate_id} role={self.role!r}>"