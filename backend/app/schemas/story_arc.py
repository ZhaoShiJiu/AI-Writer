from datetime import datetime
from pydantic import BaseModel


class StoryArcCreate(BaseModel):
    title: str
    arc_type: str = "main"  # main / sub / character
    description: str | None = None
    start_chapter_id: int | None = None
    end_chapter_id: int | None = None
    status: str = "planned"
    emotional_target: dict | None = None
    pacing_plan: dict | None = None
    scene_plan: dict | None = None


class StoryArcUpdate(BaseModel):
    title: str | None = None
    arc_type: str | None = None
    description: str | None = None
    start_chapter_id: int | None = None
    end_chapter_id: int | None = None
    status: str | None = None
    emotional_target: dict | None = None
    pacing_plan: dict | None = None
    scene_plan: dict | None = None


class StoryArcResponse(BaseModel):
    id: int
    novel_id: int
    title: str
    arc_type: str
    description: str | None
    start_chapter_id: int | None
    end_chapter_id: int | None
    status: str
    emotional_target: dict | None
    pacing_plan: dict | None
    scene_plan: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoryArcListResponse(BaseModel):
    arcs: list[StoryArcResponse]
