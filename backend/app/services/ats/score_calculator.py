import re
from datetime import datetime

class ScoreCalculator:
    @classmethod
    def calculate_experience_score(cls, text: str, action_verbs: list) -> tuple[int, int]:
        """Evaluate experience metrics.
        
        Returns:
            tuple[score, years_of_experience]
        """
        if not text:
            return 0, 0

        # Heuristic 1: Years of Experience from Date Ranges
        # Pattern: e.g. 2018 - 2022, 2021 - Present, 2020 to Current
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

        years_score = 5
        if years >= 5:
            years_score = 30
        elif 3 <= years < 5:
            years_score = 20
        elif 1 <= years < 3:
            years_score = 10

        # Heuristic 2: Number of Positions (count titles like Developer, Engineer, Architect, Lead, Manager, Analyst, Consultant)
        title_keywords = ["developer", "engineer", "architect", "lead", "manager", "analyst", "consultant", "specialist"]
        title_count = 0
        for title in title_keywords:
            title_count += len(re.findall(rf"\b{title}\b", text.lower()))

        positions_score = 5
        if title_count >= 4:
            positions_score = 20
        elif 2 <= title_count < 4:
            positions_score = 15
        elif title_count == 1:
            positions_score = 10

        # Heuristic 3: Action Verbs count
        verb_count = len(action_verbs)
        verbs_score = 5
        if verb_count >= 8:
            verbs_score = 25
        elif 5 <= verb_count < 8:
            verbs_score = 20
        elif 2 <= verb_count < 5:
            verbs_score = 10

        # Heuristic 4: Achievement Statements (containing numbers/percentages or metrics)
        # Look for numbers next to performance keywords or percentages, currency
        metrics_pattern = r"\b(?:\d+(?:\.\d+)?%\b|\$\d+|\b\d+\s*(?:percent|x|X|million|billion)\b)"
        metrics_found = re.findall(metrics_pattern, text)
        achievement_words = ["reduced", "increased", "improved", "optimized", "saved", "revenue", "saved", "launched", "delivered"]
        ach_word_count = sum(1 for w in achievement_words if w in text.lower())
        
        # Combine metric matches and action achievement verbs
        achievement_count = len(metrics_found) + (ach_word_count // 2)
        ach_score = 5
        if achievement_count >= 4:
            ach_score = 25
        elif 2 <= achievement_count < 4:
            ach_score = 20
        elif achievement_count == 1:
            ach_score = 15

        total_experience_score = years_score + positions_score + verbs_score + ach_score
        return min(100, total_experience_score), years

    @classmethod
    def calculate_projects_score(cls, text: str, tech_skills: list) -> int:
        """Evaluate projects metrics.
        
        Returns:
            score (0-100)
        """
        if not text:
            return 0

        text_lower = text.lower()
        
        # Heuristic 1: Project count estimation
        # Count explicit project keywords or headers
        project_mentions = len(re.findall(r"\bproject\b", text_lower))
        project_count_score = 10
        if project_mentions >= 4:
            project_count_score = 40
        elif 2 <= project_mentions < 4:
            project_count_score = 30
        elif project_mentions == 1:
            project_count_score = 20

        # Heuristic 2: Tech stack utilization in descriptions
        # Count how many of the candidate's skills are mentioned near project keywords (or generally in text)
        tech_count = len(tech_skills)
        tech_score = 5
        if tech_count >= 6:
            tech_score = 30
        elif 3 <= tech_count < 6:
            tech_score = 20
        elif tech_count >= 1:
            tech_score = 10

        # Heuristic 3: Project description detail / word length
        # Check if project paragraphs are descriptive (at least 60 words describing projects)
        words_count = len(text.split())
        desc_score = 5
        if words_count > 400 and project_mentions >= 1:
            desc_score = 30
        elif words_count > 200:
            desc_score = 20
        elif words_count > 100:
            desc_score = 10

        return min(100, project_count_score + tech_score + desc_score)

    @classmethod
    def calculate_education_score(cls, text: str) -> int:
        """Evaluate education credentials.
        
        Returns:
            score (0-100)
        """
        if not text:
            return 0

        text_lower = text.lower()

        # Heuristic 1: Degree
        degree_keywords = ["bachelor", "master", "phd", "b.sc", "b.s", "m.sc", "m.s", "b.tech", "m.tech", "degree", "diploma", "graduate", "bs", "ms", "mba"]
        has_degree = any(re.search(rf"\b{d}\b", text_lower) for d in degree_keywords)
        degree_score = 40 if has_degree else 10

        # Heuristic 2: Institution
        inst_keywords = ["university", "college", "institute", "academy", "school", "polytechnic"]
        has_inst = any(inst in text_lower for inst in inst_keywords)
        inst_score = 40 if has_inst else 10

        # Heuristic 3: Graduation Year
        # 4 digit year between 1990 and 2032
        year_match = re.search(r"\b(199\d|20[0-2]\d|203[0-2])\b", text)
        year_score = 20 if year_match else 0

        return degree_score + inst_score + year_score

    @classmethod
    def calculate_grammar_score(cls, text: str) -> dict:
        """Evaluate grammar, readability, and punctuation quality.
        
        Returns:
            dict containing:
                - score: overall grammar score (0-100)
                - typos_found: list of typo descriptions
        """
        if not text:
            return {"score": 0, "typos_found": ["Empty text"]}

        feedback = []

        # Readability check: Average sentence length
        # Split by sentence-ending punctuation (. ! ?)
        sentences = [s.strip() for s in re.split(r"[\.\!\?]+", text) if s.strip()]
        sentence_count = len(sentences)
        words = text.split()
        word_count = len(words)

        avg_sentence_len = word_count / sentence_count if sentence_count > 0 else 0
        
        readability_score = 20
        if 10 <= avg_sentence_len <= 25:
            readability_score = 50
        elif 5 <= avg_sentence_len < 10 or 25 < avg_sentence_len <= 35:
            readability_score = 40
            feedback.append(f"Average sentence length is {avg_sentence_len:.1f} words. Aim for 10-25 words for best readability.")
        else:
            readability_score = 25
            feedback.append("Sentences are either too short and choppy or excessively long. Aim for moderate sentence lengths.")

        # Heuristic checks: spacing and punctuation issues
        spacing_penalty = 0
        # 1. Double spaces
        double_spaces = len(re.findall(r"  +", text))
        if double_spaces > 0:
            spacing_penalty += min(15, double_spaces * 3)
            feedback.append(f"Found {double_spaces} double spaces. Ensure single spacing between words.")

        # 2. Missing space after punctuation (e.g. word.word)
        missing_space_punctuation = len(re.findall(r"\b[a-zA-Z]+\.[a-zA-Z]+\b", text))
        if missing_space_punctuation > 0:
            spacing_penalty += min(15, missing_space_punctuation * 3)
            feedback.append("Punctuation spacing issue: Found missing spaces after periods.")

        # 3. Sentence capitalization checks
        capitalization_errors = 0
        for s in sentences:
            # Check if first character is lowercase
            first_char = s[0]
            if first_char.isalpha() and first_char.islower():
                capitalization_errors += 1
        
        capitalization_penalty = 0
        if capitalization_errors > 0:
            capitalization_penalty = min(20, capitalization_errors * 4)
            feedback.append(f"Found {capitalization_errors} sentences starting with a lowercase letter.")

        punctuation_score = max(0, 50 - spacing_penalty - capitalization_penalty)
        final_grammar_score = readability_score + punctuation_score

        return {
            "score": min(100, int(final_grammar_score)),
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
