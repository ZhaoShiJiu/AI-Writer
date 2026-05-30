from datetime import datetime
from pydantic import BaseModel


class ForeshadowingCreate(BaseModel):
    name: str
    description: str | None = None
    planted_at_chapter_id: int | None = None
    payoff_at_chapter_id: int | None = None
    status: str = "planned"  # planned / planted / reminded / payoff
    content_snippet: str | None = None
    notes: str | None = None


class ForeshadowingUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    planted_at_chapter_id: int | None = None
    payoff_at_chapter_id: int | None = None
    status: str | None = None
    content_snippet: str | None = None
    notes: str | None = None


class ForeshadowingResponse(BaseModel):
    id: int
    novel_id: int
    name: str
    description: str | None
    planted_at_chapter_id: int | None
    payoff_at_chapter_id: int | None
    status: str
    content_snippet: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ForeshadowingListResponse(BaseModel):
    foreshadowings: list[ForeshadowingResponse]
