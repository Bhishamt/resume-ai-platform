import re
from typing import List, Dict

class SkillMatcher:
    @classmethod
    def _contains_skill(cls, text_lower: str, skill: str) -> bool:
        skill_lower = skill.lower().strip()
        if not skill_lower:
            return False
        
        escaped_skill = re.escape(skill_lower)
        
        if skill_lower.endswith("++") or skill_lower.endswith("#"):
            pattern = rf"\b{escaped_skill}"
        elif skill_lower.startswith("."):
            pattern = rf"{escaped_skill}\b"
        else:
            pattern = rf"\b{escaped_skill}\b"
            
        return re.search(pattern, text_lower) is not None

    @classmethod
    def match_skills(cls, resume_text: str, required_skills: List[str], preferred_skills: List[str]) -> Dict:
        """Match candidate's resume text against job description skills.
        
        Returns:
            Dict containing scores, matched/missing lists, and explanations.
        """
        if not resume_text:
            return {
                "score": 0,
                "weighted_score": 0.0,
                "matching_skills": [],
                "missing_skills": required_skills,
                "matching_preferred": [],
                "missing_preferred": preferred_skills,
                "reasons": [{"rule": "Resume text is empty", "points": -40.0}]
            }

        text_lower = resume_text.lower()
        
        matching_required = []
        missing_required = []
        for skill in required_skills:
            if cls._contains_skill(text_lower, skill):
                matching_required.append(skill)
            else:
                missing_required.append(skill)

        matching_preferred = []
        missing_preferred = []
        for skill in preferred_skills:
            if cls._contains_skill(text_lower, skill):
                matching_preferred.append(skill)
            else:
                missing_preferred.append(skill)

        required_count = len(required_skills)
        preferred_count = len(preferred_skills)

        req_score = 100.0
        if required_count > 0:
            req_score = (len(matching_required) / required_count) * 100.0

        pref_score = 100.0
        if preferred_count > 0:
            pref_score = (len(matching_preferred) / preferred_count) * 100.0

        if required_count > 0 and preferred_count > 0:
            category_score = (req_score * 0.8) + (pref_score * 0.2)
        elif required_count > 0:
            category_score = req_score
        elif preferred_count > 0:
            category_score = pref_score
        else:
            category_score = 100.0

        weighted_score = (category_score / 100.0) * 40.0

        # Generate explanations (deductions out of 40 points)
        reasons = []
        
        if required_count > 0:
            req_pool = 32.0 if preferred_count > 0 else 40.0
            pts_per_req = req_pool / required_count
            for skill in matching_required:
                reasons.append({"rule": f"{skill} matched", "points": 0.0})
            for skill in missing_required:
                reasons.append({"rule": f"{skill} missing", "points": -round(pts_per_req, 2)})
                
        if preferred_count > 0:
            pref_pool = 8.0
            pts_per_pref = pref_pool / preferred_count
            for skill in matching_preferred:
                reasons.append({"rule": f"{skill} matched (preferred)", "points": 0.0})
            for skill in missing_preferred:
                reasons.append({"rule": f"{skill} missing (preferred)", "points": -round(pts_per_pref, 2)})

        return {
            "score": int(round(category_score)),
            "weighted_score": round(weighted_score, 2),
            "matching_skills": matching_required + matching_preferred,
            "missing_skills": missing_required,
            "matching_preferred": matching_preferred,
            "missing_preferred": missing_preferred,
            "reasons": reasons
        }
