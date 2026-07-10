from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class DashboardPreferencesUpdate(BaseModel):
    layout: Optional[List[str]] = Field(None, description="Ordered widget ID list")
    widgets: Optional[Dict[str, bool]] = Field(None, description="Widget toggling state map")
    theme: Optional[str] = Field(None, description="Dashboard interface theme")

class DashboardPreferencesResponse(BaseModel):
    layout: List[str]
    widgets: Dict[str, bool]
    theme: str
    updated_at: datetime

    model_config = {"from_attributes": True}
