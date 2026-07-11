from typing import Dict, List

from app.services.job_matching.education_matcher import EducationMatcher
from app.services.job_matching.experience_matcher import ExperienceMatcher
from app.services.job_matching.keyword_matcher import KeywordMatcher
from app.services.job_matching.recommendation_engine import RecommendationEngine
from app.services.job_matching.score_calculator import ScoreCalculator
from app.services.job_matching.similarity_engine import SimilarityEngine
from app.services.job_matching.skill_matcher import SkillMatcher


class MatchingEngine:
    @classmethod
    def match_resume_to_job(
        cls,
        resume_text: str,
        job_title: str,
        job_description: str,
        required_skills: List[str],
        preferred_skills: List[str],
        required_experience: str,
        education_requirement: str,
    ) -> Dict:
        """Run all matching checks deterministically and return detailed reports."""

        # 1. Run Skill Matcher (40% weight)
        skill_res = SkillMatcher.match_skills(
            resume_text, required_skills, preferred_skills
        )

        # 2. Run Keyword Matcher (20% weight)
        keyword_res = KeywordMatcher.match_keywords(
            resume_text, job_title, job_description
        )

        # 3. Run Experience Matcher (20% weight)
        exp_res = ExperienceMatcher.match_experience(
            resume_text, required_experience, job_title
        )

        # 4. Run Education Matcher (10% weight)
        edu_res = EducationMatcher.match_education(resume_text, education_requirement)

        # 5. Run Similarity Engine (10% weight)
        similarity_val = SimilarityEngine.calculate_similarity(
            resume_text, job_description
        )
        sim_score, sim_weighted, sim_reasons = (
            ScoreCalculator.calculate_similarity_score(similarity_val)
        )

        # 6. Calculate Final Match Score
        {
            "Keywords": keyword_res["weighted_score"],
            "Experience": exp_res["weighted_score"],
            "Formatting": 0.0,  # Not used in job matching weights, placeholder/compatible
            "Sections": 0.0,
            "Projects": 0.0,
            "Education": edu_res["weighted_score"],
            "Grammar": 0.0,
            "Skills": skill_res["weighted_score"],
            "Similarity": sim_weighted,
        }

        # The weights sum to 100: Skills (40), Keywords (20), Experience (20), Education (10), Similarity (10)
        overall_match = ScoreCalculator.calculate_overall_match(
            {
                "Skills": skill_res["weighted_score"],
                "Keywords": keyword_res["weighted_score"],
                "Experience": exp_res["weighted_score"],
                "Education": edu_res["weighted_score"],
                "Similarity": sim_weighted,
            }
        )

        # 7. Generate Recommendations & Priority
        recs = RecommendationEngine.generate_recommendations(
            overall_score=overall_match,
            missing_skills=skill_res["missing_skills"],
            missing_keywords=keyword_res["missing_keywords"],
            experience_score=exp_res["score"],
            education_score=edu_res["score"],
            similarity_score=sim_score,
        )

        # 8. Compile score explanations JSON
        score_explanations = {
            "Skills": {
                "score": skill_res["weighted_score"],
                "max_score": 40.0,
                "percentage": skill_res["score"],
                "reasons": skill_res["reasons"],
            },
            "Keywords": {
                "score": keyword_res["weighted_score"],
                "max_score": 20.0,
                "percentage": keyword_res["score"],
                "reasons": keyword_res["reasons"],
            },
            "Experience": {
                "score": exp_res["weighted_score"],
                "max_score": 20.0,
                "percentage": exp_res["score"],
                "reasons": exp_res["reasons"],
            },
            "Education": {
                "score": edu_res["weighted_score"],
                "max_score": 10.0,
                "percentage": edu_res["score"],
                "reasons": edu_res["reasons"],
            },
            "Similarity": {
                "score": sim_weighted,
                "max_score": 10.0,
                "percentage": sim_score,
                "reasons": sim_reasons,
            },
        }

        return {
            "overall_match": overall_match,
            "skill_match": skill_res["score"],
            "experience_match": exp_res["score"],
            "education_match": edu_res["score"],
            "keyword_match": keyword_res["score"],
            "matching_skills": skill_res["matching_skills"],
            "missing_skills": skill_res["missing_skills"],
            "missing_keywords": keyword_res["missing_keywords"],
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "recommendations": recs["recommendations"],
            "score_explanations": score_explanations,
            "improvement_priority": recs["improvement_priority"],
        }
