from dataclasses import dataclass, field

from app.services.text_utils import normalize_skill, parse_experience_range, parse_candidate_total_experience


@dataclass
class SkillScoreResult:
    score: float               # 0.0 - 1.0
    matched_skills: list[str]
    missing_skills: list[str]


@dataclass
class ExperienceScoreResult:
    score: float                # 0.0 - 1.0
    candidate_years: float
    required_range: tuple[float, float] | None


@dataclass
class EducationScoreResult:
    score: float                # 0.0 - 1.0
    matched_degree: str | None


@dataclass
class RuleBasedScoreResult:
    skills: SkillScoreResult
    tech: SkillScoreResult
    experience: ExperienceScoreResult
    education: EducationScoreResult
    weighted_total: float       # combined score out of the 4 metrics' weights (0.65 max)


class RuleBasedScoringService:
   

    def __init__(
        self,
        weight_skills: float = 0.25,
        weight_tech: float = 0.20,
        weight_experience: float = 0.15,
        weight_education: float = 0.05,
    ):
        self.weight_skills = weight_skills
        self.weight_tech = weight_tech
        self.weight_experience = weight_experience
        self.weight_education = weight_education

    # ------------------------------------------------------------------
    # SKILL MATCHING (also reused for "tech" — same mechanism, different
    # weight and typically a subset of skills flagged as tech-stack items)
    # ------------------------------------------------------------------

    def _merge_candidate_skills(
        self, candidate_skills: list, skill_list: list[str]
    ) -> list[str]:
      
        raw_skills: set[str] = set()

        for cs in candidate_skills:
            if cs.skills:
                raw_skills.add(cs.skills)

        for s in skill_list:
            if s:
                raw_skills.add(s)

        # Dedupe on normalized form but keep one original-cased version
        seen_normalized: dict[str, str] = {}
        for skill in raw_skills:
            norm = normalize_skill(skill)
            if norm and norm not in seen_normalized:
                seen_normalized[norm] = skill

        return list(seen_normalized.values())

    def score_skills(
        self, candidate_skills: list, skill_list: list[str], required_skills: list[str]
    ) -> SkillScoreResult:
        
        merged_candidate_skills = self._merge_candidate_skills(candidate_skills, skill_list)
        candidate_normalized = {normalize_skill(s) for s in merged_candidate_skills}

        matched: list[str] = []
        missing: list[str] = []

        for req_skill in required_skills:
            req_norm = normalize_skill(req_skill)
            if not req_norm:
                continue
            if req_norm in candidate_normalized:
                matched.append(req_skill)
            else:
                missing.append(req_skill)

        total_required = len(matched) + len(missing)
        score = (len(matched) / total_required) if total_required > 0 else 0.0

        return SkillScoreResult(score=round(score, 4), matched_skills=matched, missing_skills=missing)

    # ------------------------------------------------------------------
    # EXPERIENCE MATCHING
    # ------------------------------------------------------------------

    def score_experience(
        self,
        key_experience: str | None,
        key_experience_in_month: str | None,
        min_experience_raw: str | None,
        max_experience_raw: str | None,
    ) -> ExperienceScoreResult:
       
        candidate_years = parse_candidate_total_experience(key_experience, key_experience_in_month)

        min_parsed = parse_experience_range(min_experience_raw)
        max_parsed = parse_experience_range(max_experience_raw)

        required_min = min_parsed[0] if min_parsed else None
        required_max = max_parsed[1] if max_parsed else None

        if required_min is None and required_max is None:
            # No requirement specified — can't penalize, treat as neutral pass
            return ExperienceScoreResult(score=1.0, candidate_years=candidate_years, required_range=None)

        required_min = required_min or 0.0
        required_max = required_max or 99.0

        if required_min <= candidate_years <= required_max:
            score = 1.0
        elif candidate_years < required_min:
            # Partial credit scaling down to 0 as gap grows past 2 years short
            gap = required_min - candidate_years
            score = max(0.0, 1.0 - (gap / 2.0))
        else:
            # Overqualified — small penalty, not a hard fail
            gap = candidate_years - required_max
            score = max(0.5, 1.0 - (gap / 10.0))

        return ExperienceScoreResult(
            score=round(score, 4),
            candidate_years=candidate_years,
            required_range=(required_min, required_max),
        )

    # ------------------------------------------------------------------
    # EDUCATION MATCHING
    # ------------------------------------------------------------------

    def score_education(
        self, education_records: list, min_qualification: str | None, preferred_qualification: str | None
    ) -> EducationScoreResult:
        
        candidate_degrees = [
            e.degree_name.strip() for e in education_records if e.degree_name and e.degree_name.strip()
        ]

        if not candidate_degrees:
            return EducationScoreResult(score=0.0, matched_degree=None)

        if not min_qualification and not preferred_qualification:
            # No requirement — neutral pass since candidate has *some* degree on file
            return EducationScoreResult(score=1.0, matched_degree=candidate_degrees[0])

        target_quals = [q for q in [preferred_qualification, min_qualification] if q]

        for degree in candidate_degrees:
            degree_norm = normalize_skill(degree)
            for qual in target_quals:
                qual_norm = normalize_skill(qual)
                # Loose substring match in either direction
                if qual_norm in degree_norm or degree_norm in qual_norm:
                    is_preferred = preferred_qualification and normalize_skill(preferred_qualification) == qual_norm
                    return EducationScoreResult(
                        score=1.0 if is_preferred else 0.75,
                        matched_degree=degree,
                    )

        # Has a degree, just doesn't match requirement — partial credit
        return EducationScoreResult(score=0.3, matched_degree=candidate_degrees[0])

    # ------------------------------------------------------------------
    # ORCHESTRATOR
    # ------------------------------------------------------------------

    def score_candidate_against_job(self, candidate_profile: dict, job_profile: dict) -> RuleBasedScoreResult:
        
        candidate = candidate_profile["candidate"]
        job = job_profile["job"]

        skills_result = self.score_skills(
            candidate_skills=candidate_profile["skills"],
            skill_list=candidate_profile["skill_list"],
            required_skills=job_profile["required_skills"],
        )

        # Tech uses the same matching mechanism against the same required
        # skills list for now, since jobs_required_skills doesn't separate
        # "skills" from "tech stack" as distinct fields in this schema.
        tech_result = self.score_skills(
            candidate_skills=candidate_profile["skills"],
            skill_list=candidate_profile["skill_list"],
            required_skills=job_profile["required_skills"],
        )

        experience_result = self.score_experience(
            key_experience=candidate.key_experience,
            key_experience_in_month=candidate.key_experience_in_month,
            min_experience_raw=job.minimum_experience,
            max_experience_raw=job.maximum_experience,
        )

        education_result = self.score_education(
            education_records=candidate_profile["education"],
            min_qualification=job.minimum_qualification,
            preferred_qualification=job.preffered_qualification,
        )

        weighted_total = (
            skills_result.score * self.weight_skills
            + tech_result.score * self.weight_tech
            + experience_result.score * self.weight_experience
            + education_result.score * self.weight_education
        )

        return RuleBasedScoreResult(
            skills=skills_result,
            tech=tech_result,
            experience=experience_result,
            education=education_result,
            weighted_total=round(weighted_total, 4),
        )