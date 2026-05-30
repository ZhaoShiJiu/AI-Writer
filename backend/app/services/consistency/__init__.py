"""Consistency Engine — high-level service wrapping ConsistencyAgent."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agents.consistency import ConsistencyAgent

logger = logging.getLogger(__name__)


class ConsistencyEngine:
    """Runs consistency checks and maintains check history."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_precheck(self, state: dict) -> dict:
        """Run pre-generation consistency check on the writing plan."""
        agent = ConsistencyAgent()
        result = await agent.precheck(state)
        return result.get("consistency_pre", {"passed": True, "issues": [], "overall_score": 10.0, "check_type": "pre"})

    async def run_postcheck(self, state: dict) -> dict:
        """Run post-generation consistency check on generated text."""
        agent = ConsistencyAgent()
        result = await agent.think(state)
        return result.get("consistency_post", {"passed": True, "issues": [], "overall_score": 10.0, "check_type": "post"})

    async def get_consistency_history(self, novel_id: int, limit: int = 10) -> list[dict]:
        """Get recent consistency check reports (from generation_contexts table)."""
        # For now, return empty — reports are stored in generation_contexts
        return []
