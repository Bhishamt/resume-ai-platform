class RecommendationEngine:
    @classmethod
    def generate_recommendations(
        cls,
        category_scores: dict,
        detected_sections: list,
        missing_sections: list,
        found_keywords: dict,
        missing_keywords: list,
        formatting_details: dict,
        formatting_feedback: list,
        grammar_feedback: list,
    ) -> dict:
        """Analyze score details to produce qualitative strengths, weaknesses, and suggestions.

        Returns:
            dict containing:
                - strengths: list of strings
                - weaknesses: list of strings
                - suggestions: list of strings
        """
        strengths = []
        weaknesses = []
        suggestions = []

        # 1. Evaluate Strengths
        if category_scores.get("keyword_score", 0) >= 70:
            strengths.append("Strong keyword alignment and rich technical vocabulary.")
        if category_scores.get("experience_score", 0) >= 70:
            strengths.append(
                "Demonstrated professional experience supported by action verbs."
            )
        if category_scores.get("formatting_score", 0) >= 80:
            strengths.append(
                "Excellent layout structure, page-length, and contact clarity."
            )
        if category_scores.get("projects_score", 0) >= 70:
            strengths.append(
                "Clear project descriptions showcasing practical application of tools."
            )
        if category_scores.get("section_score", 0) >= 80:
            strengths.append(
                "Comprehensive sections covering standard professional headers."
            )
        if category_scores.get("grammar_score", 0) >= 80:
            strengths.append(
                "High readability level with proper sentence and punctuation flow."
            )

        if not strengths:
            strengths.append("Clear base layout containing standard resume sections.")

        # 2. Evaluate Weaknesses
        if category_scores.get("keyword_score", 0) < 60:
            weaknesses.append("Low density of high-value industry skills and keywords.")
        if category_scores.get("experience_score", 0) < 60:
            weaknesses.append(
                "Weak positioning of professional achievements and work history."
            )
        if category_scores.get("formatting_score", 0) < 70:
            weaknesses.append(
                "Suboptimal formatting, missing contact details, or excessive length."
            )
        if category_scores.get("projects_score", 0) < 60:
            weaknesses.append(
                "Sparse project descriptions or limited technology stack details."
            )
        if missing_sections:
            weaknesses.append(
                f"Missing core professional sections: {', '.join(missing_sections)}."
            )
        if category_scores.get("grammar_score", 0) < 70:
            weaknesses.append(
                "Choppy sentence structures or visible capitalization/spacing errors."
            )
        if len(missing_keywords) >= 3:
            weaknesses.append(
                f"Missing recommended technical keywords: {', '.join(missing_keywords[:4])}."
            )

        if not weaknesses:
            weaknesses.append(
                "Slightly low keyword density compared to top-tier candidates."
            )

        # 3. Evaluate Suggestions
        if category_scores.get("keyword_score", 0) < 75:
            suggestions.append(
                "Incorporate more technical tools and soft skills in the Skills section."
            )
        if category_scores.get("experience_score", 0) < 75:
            suggestions.append(
                "Rewrite job descriptions using quantified achievements (e.g. %, $, numbers) instead of task lists."
            )
        if formatting_details.get("bullet_count", 0) < 8:
            suggestions.append(
                "Use bulleted lists (at least 8-10 points total) to describe your impact in work and projects."
            )
        if not formatting_details.get("has_email") or not formatting_details.get(
            "has_phone"
        ):
            suggestions.append(
                "Ensure your email and phone number are clearly visible at the top of the page."
            )
        if missing_sections:
            suggestions.append(
                f"Add sections for {', '.join(missing_sections)} to provide a complete profile."
            )
        if len(missing_keywords) > 0:
            suggestions.append(
                f"Add key technical tools to your text, such as: {', '.join(missing_keywords[:4])}."
            )
        if grammar_feedback:
            suggestions.append(
                "Proofread to fix spacing errors, double spaces, or sentence capitalization issues."
            )

        if not suggestions:
            suggestions.append(
                "Tailor keywords specifically to matching job descriptions to maximize score."
            )

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
        }
