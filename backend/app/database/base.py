# Import all models here so Alembic can detect them
from app.database.base_class import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.upload_history import UploadHistory  # noqa: F401
from app.models.analysis_report import AnalysisReport  # noqa: F401
from app.models.job_description import JobDescription  # noqa: F401
from app.models.job_match import JobMatch  # noqa: F401
from app.models.ai_feedback import AIFeedback  # noqa: F401


