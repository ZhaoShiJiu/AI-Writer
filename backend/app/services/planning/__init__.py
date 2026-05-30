"""Narrative Planning Service — wraps PlannerAgent + WritingPlanRepository."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.writing_plan import WritingPlanRepository
from app.repositories.story_arc import StoryArcRepository
from app.repositories.chapter import ChapterRepository
from app.services.agents.planner import PlannerAgent

logger = logging.getLogger(__name__)


class NarrativePlanningService:
    """High-level service for narrative planning operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.plan_repo = WritingPlanRepository(db)
        self.arc_repo = StoryArcRepository(db)
        self.chapter_repo = ChapterRepository(db)

    async def auto_analyze_novel(self, novel_id: int) -> dict:
        """Auto-analyze existing chapters to extract genre, themes, characters."""
        chapters = await self.chapter_repo.list_by_novel(novel_id)

        chapter_samples = []
        for ch in chapters:
            chapter_samples.append({
                "title": ch.title,
                "content": ch.content[:2000] if ch.content else "",
            })

        agent = PlannerAgent()
        result = await agent.auto_analyze(chapter_samples)
        logger.info("Auto-analyzed novel %d: genre=%s", novel_id, result.get("genre", "unknown"))
        return result

    async def create_plan(self, novel_id: int, plan_data: dict, chapter_id: int | None = None,
                          plan_type: str = "chapter") -> dict:
        """Save a writing plan."""
        plan = await self.plan_repo.create(novel_id, {
            "plan_json": plan_data,
            "chapter_id": chapter_id,
            "plan_type": plan_type,
        })
        return {"id": plan.id, "plan_json": plan.plan_json, "plan_type": plan.plan_type}

    async def get_latest_plan(self, novel_id: int) -> dict | None:
        """Get the most recent plan for a novel."""
        plan = await self.plan_repo.get_latest(novel_id)
        if plan:
            return {"id": plan.id, "plan_json": plan.plan_json, "plan_type": plan.plan_type}
        return None

    async def list_plans(self, novel_id: int) -> list[dict]:
        """List all plans for a novel."""
        plans = await self.plan_repo.list_by_novel(novel_id)
        return [{"id": p.id, "plan_json": p.plan_json, "plan_type": p.plan_type} for p in plans]

    async def create_arc(self, novel_id: int, data: dict) -> dict:
        """Create a story arc."""
        arc = await self.arc_repo.create(novel_id, data)
        return {
            "id": arc.id, "novel_id": arc.novel_id, "title": arc.title,
            "arc_type": arc.arc_type, "description": arc.description,
            "start_chapter_id": arc.start_chapter_id, "end_chapter_id": arc.end_chapter_id,
            "status": arc.status, "emotional_target": arc.emotional_target,
            "pacing_plan": arc.pacing_plan, "scene_plan": arc.scene_plan,
            "created_at": arc.created_at, "updated_at": arc.updated_at,
        }

    async def list_arcs(self, novel_id: int) -> list[dict]:
        """List all story arcs for a novel."""
        arcs = await self.arc_repo.list_by_novel(novel_id)
        return [{
            "id": a.id, "novel_id": a.novel_id, "title": a.title,
            "arc_type": a.arc_type, "description": a.description,
            "start_chapter_id": a.start_chapter_id, "end_chapter_id": a.end_chapter_id,
            "status": a.status, "emotional_target": a.emotional_target,
            "pacing_plan": a.pacing_plan, "scene_plan": a.scene_plan,
            "created_at": a.created_at, "updated_at": a.updated_at,
        } for a in arcs]

    async def update_arc_progress(self, arc_id: int, chapter_id: int) -> dict | None:
        """Update an arc's progress when a chapter is written."""
        arc = await self.arc_repo.update(arc_id, {
            "end_chapter_id": chapter_id,
            "status": "active",
        })
        if arc:
            return {"id": arc.id, "status": arc.status}
        return None
