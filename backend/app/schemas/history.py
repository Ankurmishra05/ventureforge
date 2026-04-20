from datetime import datetime

from pydantic import BaseModel


class GenerationHistoryItem(BaseModel):
    generation_id: int
    startup_project_id: int
    idea: str
    audience: str
    provider_used: str
    outputs: dict
    created_at: datetime
    updated_at: datetime


class GenerationHistoryResponse(BaseModel):
    items: list[GenerationHistoryItem]
