import json
import logging
from dataclasses import dataclass

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class LLMScoreResult:
    project_relevance_score: float   # 0.0 - 1.0
    contextual_fit_score: float      # 0.0 - 1.0
    reasoning: str
    weighted_total: float            # combined score out of (0.20 + 0.15) = 0.35 max


SYSTEM_PROMPT = """You are a resume screening assistant. You evaluate how well a candidate's background matches a job's requirements on two dimensions:

1. PROJECT RELEVANCE (0.0 to 1.0): How relevant is the candidate's overview/project experience to what this job actually needs done, beyond just keyword skill matches?
2. CONTEXTUAL FIT (0.0 to 1.0): Considering role, seniority, domain, and career trajectory, how well does this candidate fit the job's context overall?

You MUST respond with ONLY valid JSON, no preamble, no markdown code fences, no explanation outside the JSON. Format exactly:

{"project_relevance_score": 0.0, "contextual_fit_score": 0.0, "reasoning": "one or two sentence explanation"}

Scores must be floats between 0.0 and 1.0. Be honest and critical — do not default to high scores; a genuine mismatch should score low."""


class LLMScoringService:
    

    def __init__(
        self,
        weight_project_relevance: float = 0.20,
        weight_contextual_fit: float = 0.15,
    ):
        self.weight_project_relevance = weight_project_relevance
        self.weight_contextual_fit = weight_contextual_fit
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=0.1,
            max_tokens=300,
        )

    def _build_candidate_summary(self, candidate_profile: dict) -> str:
        candidate = candidate_profile["candidate"]
        skills = [s.skills for s in candidate_profile["skills"] if s.skills]
        skill_list = candidate_profile["skill_list"]
        all_skills = sorted(set(skills) | set(skill_list))

        education = [
            e.degree_name for e in candidate_profile["education"] if e.degree_name and e.degree_name.strip()
        ]
        work_exp = [
            f"{w.role} at {w.company_name}" for w in candidate_profile["work_experience"] if w.role
        ]

        parts = [
            f"Current designation: {candidate.current_designation or 'N/A'}",
            f"Current company: {candidate.currently_working_company_name or 'N/A'}",
            f"Skills: {', '.join(all_skills) if all_skills else 'None listed'}",
            f"Education: {', '.join(education) if education else 'None listed'}",
            f"Work history: {'; '.join(work_exp) if work_exp else 'None listed'}",
            f"Overview: {candidate.overview.strip() if candidate.overview else 'None provided'}",
        ]
        return "\n".join(parts)

    def _build_job_summary(self, job_profile: dict) -> str:
        job = job_profile["job"]
        required_skills = job_profile["required_skills"]

        parts = [
            f"Title: {job.job_title or 'N/A'}",
            f"Company: {job.company_name or 'N/A'}",
            f"Required skills: {', '.join(required_skills) if required_skills else 'None listed'}",
            f"Employment type: {job.employment_type or 'N/A'}",
            f"Work type: {job.work_type or 'N/A'}",
            f"Description: {(job.job_description or 'None provided').strip()}",
        ]
        return "\n".join(parts)

    async def score_candidate_against_job(self, candidate_profile: dict, job_profile: dict) -> LLMScoreResult:
        
        candidate_summary = self._build_candidate_summary(candidate_profile)
        job_summary = self._build_job_summary(job_profile)

        user_prompt = f"""CANDIDATE PROFILE:
{candidate_summary}

JOB REQUIREMENTS:
{job_summary}

Evaluate project relevance and contextual fit. Respond with JSON only."""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            parsed = self._parse_response(response.content)
        except Exception as e:
            logger.error(f"LLM scoring failed, falling back to neutral score: {e}")
            parsed = {
                "project_relevance_score": 0.5,
                "contextual_fit_score": 0.5,
                "reasoning": f"LLM call failed, neutral fallback score used. Error: {e}",
            }

        project_score = parsed["project_relevance_score"]
        contextual_score = parsed["contextual_fit_score"]

        weighted_total = (
            project_score * self.weight_project_relevance
            + contextual_score * self.weight_contextual_fit
        )

        return LLMScoreResult(
            project_relevance_score=project_score,
            contextual_fit_score=contextual_score,
            reasoning=parsed["reasoning"],
            weighted_total=round(weighted_total, 4),
        )

    def _parse_response(self, raw_content: str) -> dict:
       
        text = raw_content.strip()

        # Strip markdown code fences if present, despite instructions
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Last resort: try to extract JSON object via brace matching
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(text[start : end + 1])
            else:
                raise ValueError(f"Could not parse LLM response as JSON: {raw_content!r}")

        # Validate and clamp scores into [0.0, 1.0]
        project_score = max(0.0, min(1.0, float(data.get("project_relevance_score", 0.5))))
        contextual_score = max(0.0, min(1.0, float(data.get("contextual_fit_score", 0.5))))
        reasoning = str(data.get("reasoning", "No reasoning provided."))

        return {
            "project_relevance_score": project_score,
            "contextual_fit_score": contextual_score,
            "reasoning": reasoning,
        }