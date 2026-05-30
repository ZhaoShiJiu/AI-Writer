from datetime import datetime

from pydantic import BaseModel


class EmotionCurvePoint(BaseModel):
    position: int
    emotion: str
    intensity: float


class NarrativeStateResponse(BaseModel):
    id: int
    novel_id: int
    chapter_id: int
    scene_type: str | None
    tension_score: float
    emotion: str | None
    pace: str
    goal: str | None
    emotional_curve: list
    narrative_json: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NarrativeStateListResponse(BaseModel):
    states: list[NarrativeStateResponse]


class EmotionCurveSummaryPoint(BaseModel):
    chapter_id: int
    chapter_title: str
    chapter_position: int
    emotion: str | None
    tension_score: float


class EmotionCurveResponse(BaseModel):
    novel_id: int
    curve: list[EmotionCurveSummaryPoint]
