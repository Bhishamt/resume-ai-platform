import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.resume import Resume
from app.models.analysis_report import AnalysisReport
from app.models.job_description import JobDescription
from app.models.ai_feedback import AIFeedback

from app.services.ai.groq_provider import GroqProvider
from app.services.ai.prompt_templates import templates
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.response_parser import ResponseParser
from app.services.ai.cache import ai_cache
from app.services.ai.token_counter import estimate_tokens

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, provider=None):
        self.provider = provider or GroqProvider()

    async def _execute_ai_task(
        self,
        db: Session,
        user_id: UUID,
        prompt_type: str,
        variables: Dict[str, Any],
        resume_id: Optional[UUID] = None,
        analysis_id: Optional[UUID] = None,
        job_match_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Internal helper to format prompts, check cache, run provider, parse response,
        save to the database, and return results.
        """
        # 1. Fetch template
        template = templates.get(prompt_type)
        if not template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        # 2. Build prompt
        prompt_text = PromptBuilder.build(template, variables)
        system_prompt = (
            "You are a helpful AI assistant specialized in career advancement, ATS optimization, and professional writing. "
            "Always return your responses in the exact JSON format specified in the prompt. Do not include conversational "
            "preambles or postscripts. Return ONLY valid JSON."
        )

        # 3. Check Cache
        cached_result = ai_cache.get(prompt_text, self.provider.__class__.__name__, prompt_type)
        if cached_result:
            logger.info(f"Cache hit for prompt type '{prompt_type}' and provider '{self.provider.__class__.__name__}'")
            return cached_result

        # 4. Generate AI response
        ai_data = await self.provider.generate_response(
            prompt=prompt_text,
            system_prompt=system_prompt,
            json_mode=True
        )

        # 5. Parse response
        parsed_content = ResponseParser.parse_json(ai_data["response"])

        # 6. Estimate tokens if missing (fallback)
        tokens = ai_data.get("tokens", {})
        if not tokens.get("total_tokens"):
            prompt_toks = estimate_tokens(prompt_text)
            comp_toks = estimate_tokens(ai_data["response"])
            tokens = {
                "prompt_tokens": prompt_toks,
                "completion_tokens": comp_toks,
                "total_tokens": prompt_toks + comp_toks
            }

        # 7. Persist feedback to database
        db_feedback = AIFeedback(
            user_id=user_id,
            resume_id=resume_id,
            analysis_id=analysis_id,
            job_match_id=job_match_id,
            provider=self.provider.__class__.__name__,
            prompt_type=prompt_type,
            prompt_version=template.version,
            response=ai_data["response"],
            token_usage=tokens,
            response_time=ai_data["response_time"]
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        # 8. Cache response
        ai_cache.set(prompt_text, self.provider.__class__.__name__, prompt_type, parsed_content)

        return parsed_content

    async def review_resume(
        self,
        db: Session,
        user_id: UUID,
        resume_id: UUID,
        analysis_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Analyze a resume and provide feedback and recommendations.
        """
        # Fetch Resume
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found.")

        # Fetch Analysis
        analysis = None
        if analysis_id:
            analysis = db.query(AnalysisReport).filter(
                AnalysisReport.id == analysis_id, 
                AnalysisReport.resume_id == resume_id
            ).first()
        else:
            analysis = db.query(AnalysisReport).filter(
                AnalysisReport.resume_id == resume_id
            ).order_by(desc(AnalysisReport.created_at)).first()

        strengths = analysis.strengths if analysis else []
        weaknesses = analysis.weaknesses if analysis else []

        variables = {
            "resume_text": resume.parsed_text or "",
            "strengths": strengths,
            "weaknesses": weaknesses
        }

        return await self._execute_ai_task(
            db=db,
            user_id=user_id,
            prompt_type="resume_review",
            variables=variables,
            resume_id=resume_id,
            analysis_id=analysis.id if analysis else None
        )

    async def generate_cover_letter(
        self,
        db: Session,
        user_id: UUID,
        resume_id: UUID,
        job_description_id: Optional[UUID] = None,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
        job_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate variations of a cover letter for a specific job description.
        """
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found.")

        # Resolve job description details
        final_job_title = job_title or ""
        final_company_name = company_name or ""
        final_job_text = job_text or ""

        if job_description_id:
            job_desc = db.query(JobDescription).filter(
                JobDescription.id == job_description_id, 
                JobDescription.user_id == user_id
            ).first()
            if job_desc:
                final_job_title = job_desc.title
                final_company_name = job_desc.company
                final_job_text = job_desc.description

        variables = {
            "resume_text": resume.parsed_text or "",
            "job_title": final_job_title,
            "company_name": final_company_name,
            "job_text": final_job_text
        }

        return await self._execute_ai_task(
            db=db,
            user_id=user_id,
            prompt_type="cover_letter",
            variables=variables,
            resume_id=resume_id
        )

    async def improve_summary(self, db: Session, user_id: UUID, resume_id: UUID) -> Dict[str, Any]:
        """
        Generate rewritten resume summary.
        """
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found.")

        variables = {
            "resume_text": resume.parsed_text or ""
        }

        # We execute a rewrite, but we can extract better profile summaries
        rewrite_result = await self._execute_ai_task(
            db=db,
            user_id=user_id,
            prompt_type="resume_rewrite",
            variables=variables,
            resume_id=resume_id
        )
        
        # We can also do a standard review to extract better summary
        review_result = await self._execute_ai_task(
            db=db,
            user_id=user_id,
            prompt_type="resume_review",
            variables={
                "resume_text": resume.parsed_text or "",
                "strengths": [],
                "weaknesses": []
            },
            resume_id=resume_id
        )
        
        return {
            "better_summary": review_result.get("better_summary", ""),
            "stronger_bullet_points": rewrite_result.get("stronger_bullet_points", [])
        }

    async def improve_projects(self, db: Session, user_id: UUID, resume_id: UUID) -> Dict[str, Any]:
        """
        Generate better project descriptions.
        """
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found.")

        variables = {
            "resume_text": resume.parsed_text or ""
        }

        rewrite_result = await self._execute_ai_task(
            db=db,
            user_id=user_id,
            prompt_type="resume_rewrite",
            variables=variables,
            resume_id=resume_id
        )
        
        return {
            "better_project_descriptions": rewrite_result.get("better_project_descriptions", []),
            "better_action_verbs": rewrite_result.get("better_action_verbs", [])
        }

    async def prepare_interview(
        self,
        db: Session,
        user_id: UUID,
        resume_id: UUID,
        job_description_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Generate technical and behavioral interview preparation questions.
        """
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found.")

        job_text = ""
        if job_description_id:
            job_desc = db.query(JobDescription).filter(
                JobDescription.id == job_description_id, 
                JobDescription.user_id == user_id
            ).first()
            if job_desc:
                job_text = f"Title: {job_desc.title}\nCompany: {job_desc.company}\nDescription: {job_desc.description}"

        variables = {
            "resume_text": resume.parsed_text or "",
            "job_text": job_text
        }

        return await self._execute_ai_task(
            db=db,
            user_id=user_id,
            prompt_type="interview_prep",
            variables=variables,
            resume_id=resume_id
        )

    async def suggest_career(self, db: Session, user_id: UUID, resume_id: UUID) -> Dict[str, Any]:
        """
        Provide career guidance and missing technologies based on a resume.
        """
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found.")

        variables = {
            "resume_text": resume.parsed_text or ""
        }

        return await self._execute_ai_task(
            db=db,
            user_id=user_id,
            prompt_type="career_guidance",
            variables=variables,
            resume_id=resume_id
        )

    def get_history(self, db: Session, user_id: UUID) -> List[AIFeedback]:
        """
        Get all AI feedbacks for a given user.
        """
        return db.query(AIFeedback).filter(AIFeedback.user_id == user_id).order_by(desc(AIFeedback.created_at)).all()

    def delete_history_item(self, db: Session, user_id: UUID, feedback_id: UUID) -> bool:
        """
        Delete a specific AI feedback log.
        """
        feedback = db.query(AIFeedback).filter(AIFeedback.id == feedback_id, AIFeedback.user_id == user_id).first()
        if not feedback:
            return False
        db.delete(feedback)
        db.commit()
        return True

# Initialize default service
ai_service = AIService()
