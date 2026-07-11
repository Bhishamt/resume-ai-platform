from typing import Dict


class EducationMatcher:
    @classmethod
    def _get_degree_level(cls, text: str) -> tuple[int, str]:
        text_lower = text.lower()
        if any(x in text_lower for x in ["phd", "ph.d", "doctorate"]):
            return 4, "PhD"
        if any(
            x in text_lower for x in ["master", "m.s.", "m.s", "ms", "mba", "m.tech"]
        ):
            return 3, "Master's"
        if any(
            x in text_lower for x in ["bachelor", "b.s.", "b.s", "bs", "b.tech", "b.a."]
        ):
            return 2, "Bachelor's"
        if any(x in text_lower for x in ["diploma", "associate"]):
            return 1, "Associate's/Diploma"
        return 0, "None"

    @classmethod
    def match_education(cls, resume_text: str, education_requirement: str) -> Dict:
        """Evaluate candidate's education against requirements.

        Returns:
            Dict containing scores and explanations.
        """
        if not resume_text:
            return {
                "score": 0,
                "weighted_score": 0.0,
                "reasons": [{"rule": "Resume text is empty", "points": -10.0}],
            }

        reasons = []
        weighted_score = 10.0

        if not education_requirement:
            reasons.append(
                {"rule": "No educational requirement specified by job", "points": 0.0}
            )
            return {"score": 100, "weighted_score": 10.0, "reasons": reasons}

        # 1. Compare Degree Levels
        req_level, req_name = cls._get_degree_level(education_requirement)
        cand_level, cand_name = cls._get_degree_level(resume_text)

        if cand_level >= req_level:
            reasons.append(
                {
                    "rule": f"Degree requirement met: Required {req_name}, candidate has {cand_name}",
                    "points": 0.0,
                }
            )
        else:
            diff = req_level - cand_level
            deduction = 4.0 if diff == 1 else 6.0
            reasons.append(
                {
                    "rule": f"Degree mismatch: Required {req_name} but highest found is {cand_name}",
                    "points": -deduction,
                }
            )
            weighted_score -= deduction

        # 2. Check Discipline / Major
        disciplines = [
            "computer science",
            "software engineering",
            "information technology",
            "mathematics",
            "business",
            "engineering",
            "finance",
            "data science",
        ]
        edu_req_lower = education_requirement.lower()
        required_disciplines = [d for d in disciplines if d in edu_req_lower]

        if required_disciplines:
            resume_lower = resume_text.lower()
            matched_discipline = any(d in resume_lower for d in required_disciplines)
            if matched_discipline:
                reasons.append(
                    {"rule": "Discipline/Field of study matched", "points": 0.0}
                )
            else:
                reasons.append(
                    {
                        "rule": f"Discipline mismatch: Required field ({', '.join(required_disciplines)}) not found in resume",
                        "points": -4.0,
                    }
                )
                weighted_score -= 4.0

        weighted_score = max(0.0, min(10.0, weighted_score))
        category_score = (weighted_score / 10.0) * 100.0

        return {
            "score": int(round(category_score)),
            "weighted_score": round(weighted_score, 2),
            "reasons": reasons,
        }
