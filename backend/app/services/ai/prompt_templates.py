from typing import List


class PromptTemplate:
    def __init__(
        self,
        name: str,
        version: str,
        variables: List[str],
        template: str,
        expected_output: str,
    ):
        self.name = name
        self.version = version
        self.variables = variables
        self.template = template
        self.expected_output = expected_output


# 1. Resume Review Template
RESUME_REVIEW_TEMPLATE = """
You are an expert technical recruiter and resume reviewer. Review the following resume details and provide constructive feedback.
You must return your output strictly in JSON format matching the schema below.

RESUME CONTENT:
{resume_text}

EXISTING ATS METRICS (IF ANY):
Strengths: {strengths}
Weaknesses: {weaknesses}

Please review this information and generate:
1. Overall Review: A high-level summary of the resume's effectiveness.
2. Resume Improvements: Bullet points of actionable changes needed.
3. Better Summary: A rewritten, highly professional, impact-driven profile summary.
4. Better Skills: Suggestions for skills to add or organize better.
5. Better Experience: Specific recommendations to elevate the work experience descriptions.
6. Better Projects: Re-phrased project bullet points emphasizing business impact and tech stack.

Expected JSON Output Schema:
{{
  "overall_review": "...",
  "resume_improvements": ["...", "..."],
  "better_summary": "...",
  "better_skills": ["...", "..."],
  "better_experience": "...",
  "better_projects": ["...", "..."]
}}
"""

resume_review = PromptTemplate(
    name="resume_review",
    version="1.0.0",
    variables=["resume_text", "strengths", "weaknesses"],
    template=RESUME_REVIEW_TEMPLATE,
    expected_output='{"overall_review": "string", "resume_improvements": "list", "better_summary": "string", "better_skills": "list", "better_experience": "string", "better_projects": "list"}',
)

# 2. Cover Letter Template
COVER_LETTER_TEMPLATE = """
You are an expert career coach. Write a customized professional cover letter based on the user's resume and target job details.
You must return your output strictly in JSON format matching the schema below.

RESUME:
{resume_text}

TARGET JOB DETAILS:
Title: {job_title}
Company: {company_name}
Description/Requirements: {job_text}

Generate three variations of the cover letter:
1. Professional Cover Letter: A standard, high-quality professional version.
2. Company-specific version: Tailored specifically to the company's domain and values mentioned.
3. ATS-friendly version: Structured with clear keywords matching the job description to pass ATS filters.

Expected JSON Output Schema:
{{
  "professional_cover_letter": "...",
  "company_specific_version": "...",
  "ats_friendly_version": "..."
}}
"""

cover_letter = PromptTemplate(
    name="cover_letter",
    version="1.0.0",
    variables=["resume_text", "job_title", "company_name", "job_text"],
    template=COVER_LETTER_TEMPLATE,
    expected_output='{"professional_cover_letter": "string", "company_specific_version": "string", "ats_friendly_version": "string"}',
)

# 3. Resume Rewrite Template
RESUME_REWRITE_TEMPLATE = """
You are an expert resume writer. Rewrite the bullet points, action verbs, and project descriptions of the following resume to make them significantly stronger, focusing on achievements (using the STAR method: Situation, Task, Action, Result) and business impact.
You must return your output strictly in JSON format matching the schema below.

RESUME CONTENT:
{resume_text}

Generate:
1. Stronger Bullet Points: Rewritten bullet points for work experience.
2. Better Action Verbs: A list of powerful, industry-recognized action verbs that fit their profile.
3. Better Project Descriptions: Stronger, technical, and result-oriented descriptions for their projects.

Expected JSON Output Schema:
{{
  "stronger_bullet_points": ["...", "..."],
  "better_action_verbs": ["...", "..."],
  "better_project_descriptions": ["...", "..."]
}}
"""

resume_rewrite = PromptTemplate(
    name="resume_rewrite",
    version="1.0.0",
    variables=["resume_text"],
    template=RESUME_REWRITE_TEMPLATE,
    expected_output='{"stronger_bullet_points": "list", "better_action_verbs": "list", "better_project_descriptions": "list"}',
)

# 4. Interview Preparation Template
INTERVIEW_PREP_TEMPLATE = """
You are an experienced technical interviewer. Generate mock interview questions based on the candidate's resume and target job details.
You must return your output strictly in JSON format matching the schema below.

RESUME:
{resume_text}

TARGET JOB DETAILS (IF ANY):
Job Details: {job_text}

Generate questions in these categories, including suggested answers or talking points for each question:
1. Technical Questions: Focus on core technologies, languages, and technical frameworks in the resume/job.
2. HR Questions: Common cultural fit, salary expectation handling, or introduction questions.
3. Behavioral Questions: Scenario-based questions (e.g., conflict resolution, leadership, handling failure).
4. Resume-based Questions: Probing questions about their specific past projects, achievements, and career transitions.

Expected JSON Output Schema:
{{
  "technical_questions": [
    {{"question": "...", "suggested_answer": "..."}}
  ],
  "hr_questions": [
    {{"question": "...", "suggested_answer": "..."}}
  ],
  "behavioral_questions": [
    {{"question": "...", "suggested_answer": "..."}}
  ],
  "resume_based_questions": [
    {{"question": "...", "suggested_answer": "..."}}
  ]
}}
"""

interview_prep = PromptTemplate(
    name="interview_prep",
    version="1.0.0",
    variables=["resume_text", "job_text"],
    template=INTERVIEW_PREP_TEMPLATE,
    expected_output='{"technical_questions": "list", "hr_questions": "list", "behavioral_questions": "list", "resume_based_questions": "list"}',
)

# 5. Career Guidance Template
CAREER_GUIDANCE_TEMPLATE = """
You are a senior career advisor. Analyze this resume and suggest next career steps, roadmaps, and skills.
You must return your output strictly in JSON format matching the schema below.

RESUME CONTENT:
{resume_text}

Generate:
1. Learning Roadmap: A step-by-step roadmap to acquire the next level of skills for their target role.
2. Missing Technologies: High-demand technologies in their target field that are currently absent from their resume.
3. Certifications: Highly valued professional certifications that would boost their profile.
4. Career Suggestions: Job roles, industry domains, or paths where they are most likely to succeed.

Expected JSON Output Schema:
{{
  "learning_roadmap": ["...", "..."],
  "missing_technologies": ["...", "..."],
  "certifications": ["...", "..."],
  "career_suggestions": ["...", "..."]
}}
"""

career_guidance = PromptTemplate(
    name="career_guidance",
    version="1.0.0",
    variables=["resume_text"],
    template=CAREER_GUIDANCE_TEMPLATE,
    expected_output='{"learning_roadmap": "list", "missing_technologies": "list", "certifications": "list", "career_suggestions": "list"}',
)

# Template registry
templates = {
    "resume_review": resume_review,
    "cover_letter": cover_letter,
    "resume_rewrite": resume_rewrite,
    "interview_prep": interview_prep,
    "career_guidance": career_guidance,
}
