import logging
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.services.parser.parser_factory import ParserFactory
from app.services.ats.section_detector import SectionDetector
from app.services.ats.keyword_analyzer import KeywordAnalyzer
from app.services.ats.formatting_checker import FormattingChecker
from app.services.ats.score_calculator import ScoreCalculator
from app.services.ats.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class AtsEngine:
    @classmethod
    def analyze_resume(cls, db: Session, resume: Resume) -> dict:
        """Analyze a resume, ensuring text is parsed/cached, running deterministic engines.
        
        Returns:
            dict with scores, strengths, weaknesses, missing_keywords, suggestions
        """
        # 1. Performance Check: Caching parsed text
        parsed_text = resume.parsed_text
        if not parsed_text:
            logger.info(f"Parsing resume on-the-fly for analysis: {resume.id}")
            try:
                parser = ParserFactory.get_parser(resume.original_filename, resume.file_type)
                parsed_data = parser.parse(resume.storage_path)
                parsed_text = parsed_data.get("raw_text", "")
                
                # Cache the parsed text back to resume
                resume.parsed_text = parsed_text
                db.add(resume)
                db.commit()
                db.refresh(resume)
            except Exception as e:
                logger.error(f"Failed to parse resume file {resume.storage_path}: {str(e)}")
                parsed_text = ""

        # Handle empty/unparsable resume text gracefully
        if not parsed_text or not parsed_text.strip():
            logger.warning(f"Empty parsed text for resume: {resume.id}")
            return {
                "ats_score": 0,
                "resume_score": 0,
                "keyword_score": 0,
                "formatting_score": 0,
                "experience_score": 0,
                "education_score": 0,
                "projects_score": 0,
                "grammar_score": 0,
                "strengths": ["Clear layout structure"],
                "weaknesses": ["Unable to extract readable text content from the file."],
                "missing_keywords": [],
                "suggestions": ["Please verify the uploaded file is not password-protected, scanned, or empty, and re-upload."]
            }

        # 2. Run Section Detector
        sections_res = SectionDetector.detect_sections(parsed_text)
        detected_sections = sections_res["detected_sections"]
        missing_sections = sections_res["missing_sections"]
        section_score = sections_res["score"]

        # 3. Run Keyword Analyzer
        keyword_res = KeywordAnalyzer.analyze_keywords(parsed_text)
        found_keywords = keyword_res["found_by_category"]
        missing_keywords = keyword_res["missing_keywords"]
        keyword_score = keyword_res["score"]

        # 4. Run Formatting Checker
        formatting_res = FormattingChecker.check_formatting(parsed_text, detected_sections)
        formatting_score = formatting_res["score"]
        formatting_details = formatting_res["details"]
        formatting_feedback = formatting_res["feedback"]

        # 5. Run Experience Evaluator
        action_verbs_found = found_keywords.get("Action Verbs", [])
        experience_score, years_of_exp = ScoreCalculator.calculate_experience_score(parsed_text, action_verbs_found)

        # 6. Run Projects Evaluator
        tech_skills_found = found_keywords.get("Technical Skills", [])
        projects_score = ScoreCalculator.calculate_projects_score(parsed_text, tech_skills_found)

        # 7. Run Education Evaluator
        education_score = ScoreCalculator.calculate_education_score(parsed_text)

        # 8. Run Grammar Evaluator
        grammar_res = ScoreCalculator.calculate_grammar_score(parsed_text)
        grammar_score = grammar_res["score"]
        grammar_feedback = grammar_res["feedback"]

        # 9. Calculate final weighted score
        category_scores = {
            "keyword_score": keyword_score,
            "experience_score": experience_score,
            "formatting_score": formatting_score,
            "projects_score": projects_score,
            "education_score": education_score,
            "grammar_score": grammar_score,
            "section_score": section_score
        }
        
        ats_score = ScoreCalculator.calculate_final_score(category_scores)
        # In this phase, we map resume_score directly to the calculated ATS score
        resume_score = ats_score

        # 10. Generate strengths, weaknesses, and suggestions
        recommendations = RecommendationEngine.generate_recommendations(
            category_scores=category_scores,
            detected_sections=detected_sections,
            missing_sections=missing_sections,
            found_keywords=found_keywords,
            missing_keywords=missing_keywords,
            formatting_details=formatting_details,
            formatting_feedback=formatting_feedback,
            grammar_feedback=grammar_feedback
        )

        return {
            "ats_score": ats_score,
            "resume_score": resume_score,
            "keyword_score": keyword_score,
            "formatting_score": formatting_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "projects_score": projects_score,
            "grammar_score": grammar_score,
            "strengths": recommendations["strengths"],
            "weaknesses": recommendations["weaknesses"],
            "missing_keywords": missing_keywords,
            "suggestions": recommendations["suggestions"]
        }
