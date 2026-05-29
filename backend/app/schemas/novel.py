from datetime import datetime

from pydantic import BaseModel


class NovelCreate(BaseModel):
    title: str


class NovelUpdate(BaseModel):
    title: str


class NovelResponse(BaseModel):
    id: int
    title: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NovelListResponse(BaseModel):
    novels: list[NovelResponse]
