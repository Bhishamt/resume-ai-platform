import re
from datetime import datetime

class ScoreCalculator:
    @classmethod
    def calculate_experience_score_explainable(cls, text: str, action_verbs: list) -> tuple[int, int, int, list]:
        """Evaluate experience metrics.
        
        Returns:
            tuple[score_out_of_100, years_of_experience, weighted_score, reasons]
        """
        if not text:
            return 0, 0, 0, [{"rule": "Resume text is empty", "points": -20}]

        # Heuristic 1: Years of Experience from Date Ranges
        current_year = datetime.now().year
        year_range_pattern = r"\b(19\d{2}|20\d{2})\s*[\-–—to\s]+\s*(19\d{2}|20\d{2}|present|current)\b"
        ranges = re.findall(year_range_pattern, text.lower())
        
        years = 0
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
            if 0 < diff < 50:  # Sanity check
                years += diff

        # If no ranges found, look for explicit statements: "5 years of experience"
        if years == 0:
            exp_statement = re.search(r"\b(\d+)\+?\s*years?\s+of\s+experience\b", text.lower())
            if exp_statement:
                years = int(exp_statement.group(1))

        # Heuristic 2: Number of Positions
        title_keywords = ["developer", "engineer", "architect", "lead", "manager", "analyst", "consultant", "specialist"]
        title_count = 0
        for title in title_keywords:
            title_count += len(re.findall(rf"\b{title}\b", text.lower()))

        # Heuristic 3: Action Verbs count
        verb_count = len(action_verbs)

        # Heuristic 4: Achievement Statements
        metrics_pattern = r"\b(?:\d+(?:\.\d+)?%\b|\$\d+|\b\d+\s*(?:percent|x|X|million|billion)\b)"
        metrics_found = re.findall(metrics_pattern, text)
        achievement_words = ["reduced", "increased", "improved", "optimized", "saved", "revenue", "saved", "launched", "delivered"]
        ach_word_count = sum(1 for w in achievement_words if w in text.lower())
        achievement_count = len(metrics_found) + (ach_word_count // 2)

        reasons = []
        weighted_score = 20

        # Years deduction (Max 6 points)
        if years >= 5:
            pass
        elif 3 <= years < 5:
            reasons.append({"rule": "Less than 5 years of experience", "points": -2})
            weighted_score -= 2
        elif 1 <= years < 3:
            reasons.append({"rule": "Less than 3 years of experience", "points": -4})
            weighted_score -= 4
        else:
            reasons.append({"rule": "No significant experience", "points": -6})
            weighted_score -= 6

        # Positions deduction (Max 4 points)
        if title_count >= 4:
            pass
        elif 2 <= title_count < 4:
            reasons.append({"rule": "Fewer than 4 positions listed", "points": -1})
            weighted_score -= 1
        elif title_count == 1:
            reasons.append({"rule": "Only 1 position listed", "points": -2})
            weighted_score -= 2
        else:
            reasons.append({"rule": "No positions listed", "points": -4})
            weighted_score -= 4

        # Action verbs deduction (Max 5 points)
        if verb_count >= 8:
            pass
        elif 5 <= verb_count < 8:
            reasons.append({"rule": "Fewer than 8 action verbs", "points": -1})
            weighted_score -= 1
        elif 2 <= verb_count < 5:
            reasons.append({"rule": "Fewer than 5 action verbs", "points": -3})
            weighted_score -= 3
        else:
            reasons.append({"rule": "Minimal action verbs", "points": -5})
            weighted_score -= 5

        # Quantifiable achievements deduction (Max 5 points)
        if achievement_count >= 4:
            pass
        elif 2 <= achievement_count < 4:
            reasons.append({"rule": "Fewer than 4 quantifiable achievements", "points": -1})
            weighted_score -= 1
        elif achievement_count == 1:
            reasons.append({"rule": "Only 1 quantifiable achievement", "points": -2})
            weighted_score -= 2
        else:
            reasons.append({"rule": "No quantifiable achievements", "points": -5})
            weighted_score -= 5

        weighted_score = max(0, min(20, weighted_score))
        score_out_of_100 = int(round(weighted_score / 0.2))

        return score_out_of_100, years, weighted_score, reasons

    @classmethod
    def calculate_experience_score(cls, text: str, action_verbs: list) -> tuple[int, int]:
        """Evaluate experience metrics (backward compatibility)."""
        score, years, _, _ = cls.calculate_experience_score_explainable(text, action_verbs)
        return score, years

    @classmethod
    def calculate_projects_score_explainable(cls, text: str, tech_skills: list) -> tuple[int, int, list]:
        """Evaluate projects metrics.
        
        Returns:
            tuple[score_out_of_100, weighted_score, reasons]
        """
        if not text:
            return 0, 0, [{"rule": "Resume text is empty", "points": -10}]

        text_lower = text.lower()
        project_mentions = len(re.findall(r"\bproject\b", text_lower))
        
        reasons = []
        weighted_score = 10

        # Project mentions deduction (Max 4 points)
        if project_mentions >= 4:
            pass
        elif 2 <= project_mentions < 4:
            reasons.append({"rule": "Fewer than 4 project mentions", "points": -1})
            weighted_score -= 1
        elif project_mentions == 1:
            reasons.append({"rule": "Only 1 project mention", "points": -2})
            weighted_score -= 2
        else:
            reasons.append({"rule": "No projects mentioned", "points": -4})
            weighted_score -= 4

        # Tech skills in projects deduction (Max 3 points)
        tech_count = len(tech_skills)
        if tech_count >= 6:
            pass
        elif 3 <= tech_count < 6:
            reasons.append({"rule": "Fewer than 6 tech skills mentioned", "points": -1})
            weighted_score -= 1
        elif 1 <= tech_count < 3:
            reasons.append({"rule": "Fewer than 3 tech skills mentioned", "points": -2})
            weighted_score -= 2
        else:
            reasons.append({"rule": "No tech skills mentioned in projects", "points": -3})
            weighted_score -= 3

        # Description detail / word length deduction (Max 3 points)
        words_count = len(text.split())
        if words_count > 400 and project_mentions >= 1:
            pass
        elif words_count > 200:
            reasons.append({"rule": "Resume text is under 400 words, project details may be brief", "points": -1})
            weighted_score -= 1
        elif words_count > 100:
            reasons.append({"rule": "Resume text is under 200 words, lacking project details", "points": -2})
            weighted_score -= 2
        else:
            reasons.append({"rule": "Resume text is under 100 words, no space for project details", "points": -3})
            weighted_score -= 3

        weighted_score = max(0, min(10, weighted_score))
        score_out_of_100 = int(round(weighted_score / 0.1))

        return score_out_of_100, weighted_score, reasons

    @classmethod
    def calculate_projects_score(cls, text: str, tech_skills: list) -> int:
        """Evaluate projects metrics (backward compatibility)."""
        score, _, _ = cls.calculate_projects_score_explainable(text, tech_skills)
        return score

    @classmethod
    def calculate_education_score_explainable(cls, text: str) -> tuple[int, int, list]:
        """Evaluate education credentials.
        
        Returns:
            tuple[score_out_of_100, weighted_score, reasons]
        """
        if not text:
            return 0, 0, [{"rule": "Resume text is empty", "points": -10}]

        text_lower = text.lower()
        reasons = []
        weighted_score = 10

        # Heuristic 1: Degree (Max 4 points deduction)
        degree_keywords = ["bachelor", "master", "phd", "b.sc", "b.s", "m.sc", "m.s", "b.tech", "m.tech", "degree", "diploma", "graduate", "bs", "ms", "mba"]
        has_degree = any(re.search(rf"\b{d}\b", text_lower) for d in degree_keywords)
        if not has_degree:
            reasons.append({"rule": "No degree keyword (Bachelor, Master, PhD, etc.) detected", "points": -4})
            weighted_score -= 4

        # Heuristic 2: Institution (Max 4 points deduction)
        inst_keywords = ["university", "college", "institute", "academy", "school", "polytechnic"]
        has_inst = any(inst in text_lower for inst in inst_keywords)
        if not has_inst:
            reasons.append({"rule": "No institution keyword (University, College, etc.) detected", "points": -4})
            weighted_score -= 4

        # Heuristic 3: Graduation Year (Max 2 points deduction)
        year_match = re.search(r"\b(199\d|20[0-2]\d|203[0-2])\b", text)
        if not year_match:
            reasons.append({"rule": "No graduation year detected", "points": -2})
            weighted_score -= 2

        weighted_score = max(0, min(10, weighted_score))
        score_out_of_100 = int(round(weighted_score / 0.1))

        return score_out_of_100, weighted_score, reasons

    @classmethod
    def calculate_education_score(cls, text: str) -> int:
        """Evaluate education credentials (backward compatibility)."""
        score, _, _ = cls.calculate_education_score_explainable(text)
        return score

    @classmethod
    def calculate_grammar_score_explainable(cls, text: str) -> tuple[int, int, list]:
        """Evaluate grammar, readability, and punctuation quality.
        
        Returns:
            tuple[score_out_of_100, weighted_score, reasons]
        """
        if not text:
            return 0, 0, [{"rule": "Resume text is empty", "points": -5}]

        # Readability check: Average sentence length
        sentences = [s.strip() for s in re.split(r"[\.\!\?]+", text) if s.strip()]
        sentence_count = len(sentences)
        words = text.split()
        word_count = len(words)
        avg_sentence_len = word_count / sentence_count if sentence_count > 0 else 0

        # Heuristic spacing and punctuation issues
        double_spaces = len(re.findall(r"  +", text))
        missing_space_punctuation = len(re.findall(r"\b[a-zA-Z]+\.[a-zA-Z]+\b", text))

        # Sentence capitalization checks
        capitalization_errors = 0
        for s in sentences:
            first_char = s[0]
            if first_char.isalpha() and first_char.islower():
                capitalization_errors += 1

        reasons = []
        weighted_score = 5.0

        # Readability / sentence length (Max 2 points)
        if 10 <= avg_sentence_len <= 25:
            pass
        elif 5 <= avg_sentence_len < 10 or 25 < avg_sentence_len <= 35:
            reasons.append({"rule": "Average sentence length is slightly outside the optimal 10-25 range", "points": -0.5})
            weighted_score -= 0.5
        else:
            reasons.append({"rule": "Average sentence length is either too short or excessively long", "points": -1.5})
            weighted_score -= 1.5

        # Double spaces (Max 1 point)
        if double_spaces > 0:
            reasons.append({"rule": "Found multiple double spaces in text", "points": -0.5})
            weighted_score -= 0.5

        # Missing space punctuation (Max 1 point)
        if missing_space_punctuation > 0:
            reasons.append({"rule": "Found missing spaces after punctuation marks", "points": -0.5})
            weighted_score -= 0.5

        # Capitalization errors (Max 1 point)
        if capitalization_errors > 0:
            reasons.append({"rule": "Found sentences starting with a lowercase letter", "points": -0.5})
            weighted_score -= 0.5

        weighted_score = max(0.0, min(5.0, weighted_score))
        score_out_of_100 = int(round(weighted_score / 0.05))

        return score_out_of_100, weighted_score, reasons

    @classmethod
    def calculate_grammar_score(cls, text: str) -> dict:
        """Evaluate grammar, readability, and punctuation quality (backward compatibility)."""
        score_out_of_100, _, reasons = cls.calculate_grammar_score_explainable(text)
        feedback = [r["rule"] for r in reasons]
        return {
            "score": score_out_of_100,
            "feedback": feedback
        }

    @classmethod
    def calculate_final_score(cls, category_scores: dict) -> int:
        """Calculate weighted final ATS score.
        
        Weights:
            Keywords: 30%
            Experience: 20%
            Formatting: 15%
            Projects: 10%
            Education: 10%
            Grammar: 5%
            Sections: 10%
        """
        weighted_score = (
            (category_scores.get("keyword_score", 0) * 0.30) +
            (category_scores.get("experience_score", 0) * 0.20) +
            (category_scores.get("formatting_score", 0) * 0.15) +
            (category_scores.get("projects_score", 0) * 0.10) +
            (category_scores.get("education_score", 0) * 0.10) +
            (category_scores.get("grammar_score", 0) * 0.05) +
            (category_scores.get("section_score", 0) * 0.10)
        )
        return int(round(weighted_score))
