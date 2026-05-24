from datetime import datetime

from pydantic import BaseModel


class ContinueRequest(BaseModel):
    user_intent: str = ""
    style_note: str = ""
    target_length: int = 400


class ContinueResponse(BaseModel):
    generation_id: int
    ai_output: str


class RegenerateRequest(BaseModel):
    user_intent: str = ""
    style_note: str = ""


class GenerationResponse(BaseModel):
    id: int
    chapter_id: int
    user_intent: str | None
    prompt_text: str
    ai_output: str
    accepted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerationListResponse(BaseModel):
    generations: list[GenerationResponse]


class AcceptRequest(BaseModel):
    accepted: bool = True
