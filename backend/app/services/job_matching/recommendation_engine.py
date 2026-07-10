from typing import List, Dict

class RecommendationEngine:
    @classmethod
    def generate_recommendations(
        cls,
        overall_score: int,
        missing_skills: List[str],
        missing_keywords: List[str],
        experience_score: int,
        education_score: int,
        similarity_score: int
    ) -> Dict:
        """Analyze matching scores and missing gaps to generate actionable recommendations.
        
        Returns:
            Dict containing:
                - recommendations: list of strings
                - improvement_priority: "High" | "Medium" | "Low"
        """
        recommendations = []

        # 1. Evaluate missing skills
        if missing_skills:
            top_skills = missing_skills[:4]
            recommendations.append(
                f"Add these critical missing skills to your resume: {', '.join(top_skills)}."
            )

        # 2. Evaluate missing keywords
        if missing_keywords:
            top_keywords = missing_keywords[:4]
            recommendations.append(
                f"Integrate these relevant industry keywords: {', '.join(top_keywords)}."
            )

        # 3. Evaluate experience gap
        if experience_score < 70:
            recommendations.append(
                "Expand on your work history and highlight senior responsibilities or domain-specific achievements."
            )
            
        # 4. Evaluate education gap
        if education_score < 70:
            recommendations.append(
                "Ensure your degree level and major fields of study are clearly formatted in your education section."
            )

        # 5. Evaluate similarity gap
        if similarity_score < 70:
            recommendations.append(
                "Tailor your resume's vocabulary, professional summary, and project details to match the job description's phrasing."
            )

        # Fallback if everything is perfect
        if not recommendations:
            recommendations.append("Your resume aligns exceptionally well with this job description. Tailor key achievements to maximize impact.")

        # Determine priority
        if overall_score < 60:
            priority = "High"
        elif overall_score < 80:
            priority = "Medium"
        else:
            priority = "Low"

        return {
            "recommendations": recommendations,
            "improvement_priority": priority
        }
