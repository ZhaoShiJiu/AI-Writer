from datetime import datetime
from pydantic import BaseModel


class ScenePlanItem(BaseModel):
    position: int = 1
    goal: str = ""
    expected_emotion: str = "中性"
    scene_type: str = "action"
    conflict_points: list[str] = []
    characters_involved: list[str] = []
    estimated_length: int = 400


class PlanData(BaseModel):
    genre: str = ""
    themes: list[str] = []
    main_characters: list[str] = []
    scene_plan: list[ScenePlanItem] = []
    overall_arc_type: str = ""
    theme_notes: str = ""


class PlanningRequest(BaseModel):
    chapter_id: int | None = None
    plan_type: str = "chapter"  # chapter / arc / oneshot
    plan_data: PlanData | None = None
    # Manual user inputs for the planner
    manual_genre: str = ""
    manual_theme: str = ""
    manual_plot_direction: str = ""


class PlanAnalysisResult(BaseModel):
    genre: str = ""
    themes: list[str] = []
    main_characters: list[str] = []
    narrative_structure: str = ""
    suggested_arcs: list[dict] = []
    analysis_notes: str = ""


class WritingPlanResponse(BaseModel):
    id: int
    novel_id: int
    chapter_id: int | None
    plan_json: dict
    plan_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WritingPlanListResponse(BaseModel):
    plans: list[WritingPlanResponse]
