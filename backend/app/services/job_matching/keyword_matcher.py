import re
from typing import Dict

from app.services.ats.keyword_analyzer import KeywordAnalyzer


class KeywordMatcher:
    @classmethod
    def _contains_word(cls, text_lower: str, word: str) -> bool:
        word_lower = word.lower().strip()
        if not word_lower:
            return False

        escaped_word = re.escape(word_lower)
        if word_lower.endswith("++") or word_lower.endswith("#"):
            pattern = rf"\b{escaped_word}"
        elif word_lower.startswith("."):
            pattern = rf"{escaped_word}\b"
        else:
            pattern = rf"\b{escaped_word}\b"

        return re.search(pattern, text_lower) is not None

    @classmethod
    def match_keywords(
        cls, resume_text: str, job_title: str, job_description: str
    ) -> Dict:
        """Find overlap of predefined keywords between job description and resume.

        Returns:
            Dict containing scores, list of matching/missing keywords, and explanations.
        """
        if not resume_text or not job_description:
            return {
                "score": 0,
                "weighted_score": 0.0,
                "matching_keywords": [],
                "missing_keywords": [],
                "reasons": [
                    {"rule": "Resume or job description is empty", "points": -20.0}
                ],
            }

        resume_lower = resume_text.lower()
        job_lower = (job_title + " " + job_description).lower()

        # 1. Identify which vocabulary keywords are present in the Job Description
        job_keywords = []
        for category, terms in KeywordAnalyzer.KEYWORDS_BY_CATEGORY.items():
            for term in terms:
                if cls._contains_word(job_lower, term):
                    # Nicely formatted display name
                    display_term = term.title() if len(term) > 3 else term.upper()
                    if term == "node.js":
                        display_term = "Node.js"
                    elif term == "ci/cd":
                        display_term = "CI/CD"
                    elif term == "rest api":
                        display_term = "REST API"
                    elif term == "fastapi":
                        display_term = "FastAPI"
                    job_keywords.append(display_term)

        job_keywords = sorted(list(set(job_keywords)))

        # Fallback to critical keywords if none are found in the job description description
        if not job_keywords:
            job_keywords = [
                kw.title() if len(kw) > 3 else kw.upper()
                for kw in KeywordAnalyzer.CRITICAL_KEYWORDS
            ]

        # 2. Check which job keywords are present in the resume
        matching_keywords = []
        missing_keywords = []
        for kw in job_keywords:
            if cls._contains_word(resume_lower, kw):
                matching_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        # 3. Calculate Scores (Max 20 points)
        total_count = len(job_keywords)
        matched_count = len(matching_keywords)

        category_score = (
            (matched_count / total_count) * 100.0 if total_count > 0 else 100.0
        )
        weighted_score = (category_score / 100.0) * 20.0

        # 4. Generate Explanations
        reasons = []
        pts_per_keyword = 20.0 / total_count if total_count > 0 else 0.0

        for kw in matching_keywords:
            reasons.append({"rule": f"{kw} keyword matched", "points": 0.0})
        for kw in missing_keywords:
            reasons.append(
                {"rule": f"Missing {kw} keyword", "points": -round(pts_per_keyword, 2)}
            )

        return {
            "score": int(round(category_score)),
            "weighted_score": round(weighted_score, 2),
            "matching_keywords": matching_keywords,
            "missing_keywords": missing_keywords,
            "reasons": reasons,
        }
