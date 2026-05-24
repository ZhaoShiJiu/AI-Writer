from datetime import datetime

from pydantic import BaseModel


class ChapterCreate(BaseModel):
    title: str = "未命名章节"


class ChapterUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class ChapterResponse(BaseModel):
    id: int
    novel_id: int
    title: str
    content: str
    summary: str | None
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterListResponse(BaseModel):
    chapters: list[ChapterResponse]
