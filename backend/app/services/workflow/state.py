"""Workflow state definition for LangGraph V4 pipeline."""

from typing import TypedDict


class WorkflowState(TypedDict, total=False):
    # ---- Inputs ----
    novel_id: int
    chapter_id: int
    chapter_content: str
    user_intent: str
    style_note: str
    target_length: int
    emotion_target: str | None
    pace_target: str | None
    planner_input: dict | None
    model: str

    # ---- Agent outputs (populated during workflow) ----
    intent_analysis: dict | None
    memory_context: dict | None
    graph_context: dict | None
    scene_plan: dict | None
    narrative_context: dict | None
    consistency_pre: dict | None
    generated_text: str | None
    rewritten_text: str | None
    consistency_post: dict | None

    # ---- Internal ----
    _db_session: object  # AsyncSession — passed through workflow
    _raw_memory: dict | None
    _narrative_states: list | None
    _auto_analysis: dict | None
    _retry_count: int

    # ---- Metadata ----
    current_step: str
    error: str | None
