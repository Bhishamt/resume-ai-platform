import re
from datetime import datetime
from typing import Dict

class ExperienceMatcher:
    @classmethod
    def match_experience(cls, resume_text: str, required_experience: str, job_title: str) -> Dict:
        """Evaluate candidate's experience against requirements.
        
        Returns:
            Dict containing scores, years of experience, and explanations.
        """
        if not resume_text:
            return {
                "score": 0,
                "weighted_score": 0.0,
                "candidate_years": 0,
                "required_years": 0,
                "reasons": [{"rule": "Resume text is empty", "points": -20.0}]
            }

        # 1. Extract required years from string
        req_years = 0
        if required_experience:
            match = re.search(r"(\d+)", required_experience)
            if match:
                req_years = int(match.group(1))

        # 2. Extract years of experience from resume date ranges
        current_year = datetime.now().year
        year_range_pattern = r"\b(19\d{2}|20\d{2})\s*[\-–—to\s]+\s*(19\d{2}|20\d{2}|present|current)\b"
        ranges = re.findall(year_range_pattern, resume_text.lower())
        
        candidate_years = 0
        for start, end in ranges:
            start_yr = int(start)
            if end in ["present", "current"]:
                end_yr = current_year
            else:
                try:
                    end_yr = int(end)
                except ValueError:
                    end_yr = current_year
            
            diff = end_yr - start_yr
            if 0 < diff < 50:
                candidate_years += diff

        if candidate_years == 0:
            exp_statement = re.search(r"\b(\d+)\+?\s*years?\s+of\s+experience\b", resume_text.lower())
            if exp_statement:
                candidate_years = int(exp_statement.group(1))

        reasons = []
        weighted_score = 20.0

        # Years of experience check (Max deduction: 10 points)
        if candidate_years >= req_years:
            reasons.append({"rule": f"Meets or exceeds required experience of {req_years} years (+{candidate_years} years found)", "points": 0.0})
        else:
            missing_years = req_years - candidate_years
            deduction = min(10.0, missing_years * 2.0)
            reasons.append({"rule": f"Missing {missing_years} years of required experience", "points": -round(deduction, 2)})
            weighted_score -= deduction

        # Seniority match check (Max deduction: 4 points)
        seniority_keywords = ["senior", "lead", "principal", "manager", "director", "architect", "head", "vp"]
        job_title_lower = job_title.lower()
        required_seniority = any(s in job_title_lower for s in seniority_keywords)

        if required_seniority:
            # Check if resume text has any seniority keywords
            resume_lower = resume_text.lower()
            has_seniority = any(s in resume_lower for s in seniority_keywords)
            if has_seniority:
                reasons.append({"rule": "Seniority keyword alignment matched", "points": 0.0})
            else:
                reasons.append({"rule": "Seniority mismatch: Job requires senior-level titles but resume lacks them", "points": -4.0})
                weighted_score -= 4.0

        # Role / Domain alignment check (Max deduction: 6 points)
        # Find domains in job title and see if they appear in resume
        domain_terms = ["backend", "frontend", "fullstack", "devops", "cloud", "data", "security", "mobile", "designer", "product", "sales", "marketing", "qa", "testing"]
        found_job_domains = [d for d in domain_terms if d in job_title_lower]
        
        if found_job_domains:
            resume_lower = resume_text.lower()
            domain_match = any(d in resume_lower for d in found_job_domains)
            if domain_match:
                reasons.append({"rule": "Role/Domain alignment matched", "points": 0.0})
            else:
                reasons.append({"rule": f"Role mismatch: Missing domain keywords ({', '.join(found_job_domains)}) in resume", "points": -6.0})
                weighted_score -= 6.0

        weighted_score = max(0.0, min(20.0, weighted_score))
        category_score = (weighted_score / 20.0) * 100.0

        return {
            "score": int(round(category_score)),
            "weighted_score": round(weighted_score, 2),
            "candidate_years": candidate_years,
            "required_years": req_years,
            "reasons": reasons
        }
