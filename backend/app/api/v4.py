"""V4 API Router — Multi-Agent narrative orchestration endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.schemas.v4 import (
    V4ContinueRequest,
    V4ContinueResponse,
    GraphDataResponse,
    ConsistencyReportResponse,
    ConsistencyHistoryResponse,
    V4WorkflowStatus,
)
from app.schemas.story_arc import (
    StoryArcCreate,
    StoryArcUpdate,
    StoryArcResponse,
    StoryArcListResponse,
)
from app.schemas.foreshadowing import (
    ForeshadowingCreate,
    ForeshadowingUpdate,
    ForeshadowingResponse,
    ForeshadowingListResponse,
)
from app.schemas.plan import (
    PlanningRequest,
    PlanAnalysisResult,
    WritingPlanResponse,
    WritingPlanListResponse,
)

router = APIRouter(prefix="/api", tags=["v4"])
logger = logging.getLogger(__name__)


# ---- V4 Continue ----

@router.post("/chapters/{chapter_id}/continue-v4", response_model=V4ContinueResponse)
async def continue_chapter_v4(
    chapter_id: int,
    req: V4ContinueRequest,
    db: AsyncSession = Depends(get_db),
):
    """V4 Multi-Agent continuation — full LangGraph workflow."""
    if not settings.feature_v4_enabled:
        raise HTTPException(status_code=404, detail="V4 feature is disabled")

    from app.repositories.chapter import ChapterRepository
    from app.services.workflow.graph import get_v4_workflow
    from app.services.workflow.state import WorkflowState

    chapter_repo = ChapterRepository(db)
    chapter = await chapter_repo.get_by_id(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Build initial workflow state
    initial_state: WorkflowState = {
        "novel_id": chapter.novel_id,
        "chapter_id": chapter_id,
        "chapter_content": chapter.content or "",
        "user_intent": req.user_intent,
        "style_note": req.style_note,
        "target_length": req.target_length or settings.continuation_target_chars,
        "emotion_target": req.emotion_target,
        "pace_target": req.pace_target,
        "planner_input": req.planner_input or {},
        "model": "deepseek/deepseek-v4-pro",
        # Internal
        "_db_session": db,
        "_retry_count": 0,
    }

    # Execute LangGraph workflow
    try:
        workflow = get_v4_workflow()
        final_state = await workflow.ainvoke(initial_state)
    except Exception as e:
        logger.error("V4 workflow failed: %s", e)
        raise HTTPException(status_code=500, detail=f"V4 workflow error: {e}")

    generated_text = final_state.get("rewritten_text") or final_state.get("generated_text", "")

    if not generated_text:
        raise HTTPException(status_code=500, detail="No text generated")

    # Save generation record
    from app.models.ai_generation import AIGeneration

    generation = AIGeneration(
        chapter_id=chapter_id,
        user_intent=req.user_intent,
        prompt_text="V4 Multi-Agent Workflow",
        ai_output=generated_text,
    )
    db.add(generation)
    await db.commit()
    await db.refresh(generation)

    # Save generation context for debugging
    from app.models.generation_context import GenerationContext
    ctx = GenerationContext(
        generation_id=generation.id,
        context_json={
            "workflow_steps": final_state.get("current_step", ""),
            "intent_analysis": final_state.get("intent_analysis"),
            "consistency_pre": final_state.get("consistency_pre"),
            "consistency_post": final_state.get("consistency_post"),
        },
    )
    db.add(ctx)
    await db.commit()

    # Build workflow status for response
    workflow_status = {
        "current_step": final_state.get("current_step", ""),
        "steps": ["intent_analysis", "memory_retrieval", "story_graph_query",
                   "narrative_planning", "precheck", "writing", "rewrite",
                   "postcheck", "memory_update"],
    }

    return V4ContinueResponse(
        generation_id=generation.id,
        ai_output=generated_text,
        workflow_status=workflow_status,
    )


# ---- Story Graph ----

@router.get("/novels/{novel_id}/story-graph", response_model=GraphDataResponse)
async def get_story_graph(novel_id: int):
    """Get story graph data for frontend visualization."""
    if not settings.feature_neo4j_enabled:
        return GraphDataResponse(nodes=[], edges=[])

    from app.services.graph.story_graph import story_graph_service

    try:
        data = await story_graph_service.get_story_graph_data(novel_id)
        return GraphDataResponse(**data)
    except Exception as e:
        logger.warning("Story graph query failed: %s", e)
        return GraphDataResponse(nodes=[], edges=[])


# ---- Foreshadowings ----

@router.get("/novels/{novel_id}/foreshadowings", response_model=ForeshadowingListResponse)
async def list_foreshadowings(novel_id: int, db: AsyncSession = Depends(get_db)):
    """List all foreshadowings for a novel."""
    from app.services.foreshadowing import ForeshadowingService

    service = ForeshadowingService(db)
    items = await service.list_all(novel_id)
    return ForeshadowingListResponse(foreshadowings=items)


@router.post("/novels/{novel_id}/foreshadowings", response_model=ForeshadowingResponse)
async def create_foreshadowing(novel_id: int, data: ForeshadowingCreate, db: AsyncSession = Depends(get_db)):
    """Create a new foreshadowing manually."""
    from app.services.foreshadowing import ForeshadowingService

    service = ForeshadowingService(db)
    result = await service.create(novel_id, data.model_dump(exclude_unset=True))
    return ForeshadowingResponse(**result)


@router.put("/foreshadowings/{foreshadowing_id}", response_model=ForeshadowingResponse)
async def update_foreshadowing(foreshadowing_id: int, data: ForeshadowingUpdate, db: AsyncSession = Depends(get_db)):
    """Update a foreshadowing (status, payoff, etc.)."""
    from app.services.foreshadowing import ForeshadowingService

    service = ForeshadowingService(db)
    result = await service.update(foreshadowing_id, data.model_dump(exclude_unset=True, exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Foreshadowing not found")
    return ForeshadowingResponse(**result)


# ---- Story Arcs ----

@router.get("/novels/{novel_id}/story-arcs", response_model=StoryArcListResponse)
async def list_story_arcs(novel_id: int, db: AsyncSession = Depends(get_db)):
    """List all story arcs for a novel."""
    from app.services.planning import NarrativePlanningService

    service = NarrativePlanningService(db)
    arcs = await service.list_arcs(novel_id)
    return StoryArcListResponse(arcs=arcs)


@router.post("/novels/{novel_id}/story-arcs", response_model=StoryArcResponse)
async def create_story_arc(novel_id: int, data: StoryArcCreate, db: AsyncSession = Depends(get_db)):
    """Create a story arc."""
    from app.services.planning import NarrativePlanningService

    service = NarrativePlanningService(db)
    result = await service.create_arc(novel_id, data.model_dump(exclude_unset=True))
    return StoryArcResponse(**result)


# ---- Writing Plans ----

@router.get("/novels/{novel_id}/plans", response_model=WritingPlanListResponse)
async def list_writing_plans(novel_id: int, db: AsyncSession = Depends(get_db)):
    """List all writing plans for a novel."""
    from app.services.planning import NarrativePlanningService

    service = NarrativePlanningService(db)
    plans = await service.list_plans(novel_id)
    return WritingPlanListResponse(plans=plans)


@router.post("/novels/{novel_id}/plans", response_model=WritingPlanResponse)
async def create_writing_plan(novel_id: int, data: PlanningRequest, db: AsyncSession = Depends(get_db)):
    """Create or update a writing plan."""
    from app.services.planning import NarrativePlanningService

    service = NarrativePlanningService(db)
    plan_data = data.plan_data.model_dump() if data.plan_data else {}

    # Include manual user inputs
    if data.manual_genre:
        plan_data["manual_genre"] = data.manual_genre
    if data.manual_theme:
        plan_data["manual_theme"] = data.manual_theme
    if data.manual_plot_direction:
        plan_data["manual_plot_direction"] = data.manual_plot_direction

    result = await service.create_plan(novel_id, plan_data, data.chapter_id, data.plan_type)
    return WritingPlanResponse(**result)


# ---- Auto-Analysis ----

@router.post("/novels/{novel_id}/auto-analyze", response_model=PlanAnalysisResult)
async def auto_analyze_novel(novel_id: int, db: AsyncSession = Depends(get_db)):
    """Auto-analyze a novel to extract genre, themes, and character arcs."""
    from app.services.planning import NarrativePlanningService

    service = NarrativePlanningService(db)
    result = await service.auto_analyze_novel(novel_id)
    if not result:
        raise HTTPException(status_code=500, detail="Auto-analysis failed")
    return PlanAnalysisResult(**result)


# ---- Consistency Check ----

@router.post("/chapters/{chapter_id}/consistency-check", response_model=ConsistencyReportResponse)
async def run_consistency_check(chapter_id: int, db: AsyncSession = Depends(get_db)):
    """Run a post-hoc consistency check on a chapter."""
    from app.repositories.chapter import ChapterRepository
    from app.services.consistency import ConsistencyEngine

    chapter_repo = ChapterRepository(db)
    chapter = await chapter_repo.get_by_id(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    engine = ConsistencyEngine(db)
    state = {
        "generated_text": chapter.content or "",
        "memory_context": {},
    }

    result = await engine.run_postcheck(state)
    return ConsistencyReportResponse(**result)


@router.get("/novels/{novel_id}/consistency-history", response_model=ConsistencyHistoryResponse)
async def get_consistency_history(novel_id: int, db: AsyncSession = Depends(get_db)):
    """Get consistency check history for a novel."""
    from app.services.consistency import ConsistencyEngine

    engine = ConsistencyEngine(db)
    reports = await engine.get_consistency_history(novel_id)
    return ConsistencyHistoryResponse(reports=reports)
