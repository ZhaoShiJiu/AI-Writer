from datetime import datetime

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    id: int
    novel_id: int
    chapter_id: int | None
    summary_type: str
    summary_text: str
    characters: list = []
    important_events: list = []
    emotion: str | None
    foreshadowing: list = []
    embedding_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SummaryGenerateRequest(BaseModel):
    chapter_id: int
    force: bool = False


class SummaryListResponse(BaseModel):
    summaries: list[SummaryResponse]


class MemoryContextResponse(BaseModel):
    recent_summaries: list[SummaryResponse]
    characters: list[dict]
    world_state: dict | None
    retrieved_events: list[dict]
