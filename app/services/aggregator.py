from app.services.rule_based_scoring import RuleBasedScoreResult
from app.services.llm_scoring import LLMScoreResult

def aggregate_scores(
    candidate_id: int,
    job_id: int,
    rule_based_result: RuleBasedScoreResult,
    llm_result: LLMScoreResult,
) -> dict:
    
    final_score = round(rule_based_result.weighted_total+ llm_result.weighted_total,4)
    
    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "skills_score": rule_based_result.skills.score,
        "tech_score": rule_based_result.tech.score,
        "experience_score": rule_based_result.experience.score,
        "education_score": rule_based_result.education.score,
        "project_relevance_score": llm_result.project_relevance_score,
        "contextual_fit_score": llm_result.contextual_fit_score,
        "llm_reasoning": llm_result.reasoning,
        "final_score": final_score,
        "details":{
            "matched_skills": rule_based_result.skills.matched_skills,
            "missing_skills": rule_based_result.skills.missing_skills,
            "candidate_years": rule_based_result.experience.candidate_years,
            "required_experience_range": rule_based_result.experience.required_range,
            "matched_degree": rule_based_result.education.matched_degree,
        },
        
    }