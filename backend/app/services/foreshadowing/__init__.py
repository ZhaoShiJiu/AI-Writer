"""Foreshadowing Service — track, detect, and manage foreshadowing elements."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.foreshadowing import ForeshadowingRepository
from app.llm.client import LLMClient

logger = logging.getLogger(__name__)


class ForeshadowingService:
    """Manages foreshadowing lifecycle: plant → remind → payoff."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ForeshadowingRepository(db)

    async def list_all(self, novel_id: int) -> list[dict]:
        """List all foreshadowings for a novel."""
        items = await self.repo.list_by_novel(novel_id)
        return [_foreshadowing_to_dict(f) for f in items]

    async def list_pending(self, novel_id: int) -> list[dict]:
        """List foreshadowings that haven't been paid off yet."""
        items = await self.repo.list_pending(novel_id)
        return [_foreshadowing_to_dict(f) for f in items]

    async def create(self, novel_id: int, data: dict) -> dict:
        """Create a new foreshadowing (manual or auto-detected)."""
        f = await self.repo.create(novel_id, data)
        return _foreshadowing_to_dict(f)

    async def update(self, fid: int, data: dict) -> dict | None:
        """Update a foreshadowing (status change, payoff, etc.)."""
        f = await self.repo.update(fid, data)
        if f:
            return _foreshadowing_to_dict(f)
        return None

    async def delete(self, fid: int) -> bool:
        """Delete a foreshadowing."""
        return await self.repo.delete(fid)

    async def mark_paid_off(self, fid: int, chapter_id: int) -> dict | None:
        """Mark a foreshadowing as paid off."""
        return await self.update(fid, {
            "status": "payoff",
            "payoff_at_chapter_id": chapter_id,
        })

    async def remind(self, fid: int) -> dict | None:
        """Set foreshadowing to 'reminded' status."""
        return await self.update(fid, {"status": "reminded"})

    async def detect_from_chapter(self, novel_id: int, chapter_id: int, content: str) -> list[dict]:
        """Use LLM to detect foreshadowing elements planted in a new chapter."""
        if not content.strip():
            return []

        llm = LLMClient()
        system_prompt = """\
你是一位专业的文学分析家，擅长发现文本中埋设的伏笔。

请分析以下小说章节，找出其中埋设的伏笔元素。伏笔是指：
- 暗示未来剧情发展的线索
- 未解开的谜团
- 角色隐藏的身份或动机
- 被提及但未解释的事物
- 可能引发后续冲突的细节

返回严格 JSON 数组格式：
[
  {"name": "伏笔名称", "description": "伏笔描述", "likely_payoff_type": "可能的回收方式"}
]

如果没有明显伏笔，返回空数组 []。只返回 JSON 数组，不要其他文字。
"""

        user_prompt = content[:3000]

        try:
            text = await llm.complete(system_prompt, user_prompt)
            import re
            import json
            match = re.search(r"\[.*\]", text, re.DOTALL)
            items = json.loads(match.group()) if match else []
        except Exception:
            return []

        # Save detected foreshadowings
        results = []
        for item in items:
            try:
                f = await self.repo.create(novel_id, {
                    "name": item.get("name", "未命名伏笔"),
                    "description": item.get("description", ""),
                    "planted_at_chapter_id": chapter_id,
                    "status": "planted",
                    "content_snippet": content[:200],
                    "notes": item.get("likely_payoff_type", ""),
                })
                results.append(_foreshadowing_to_dict(f))
            except Exception:
                pass

        logger.info("Detected %d foreshadowings in chapter %d", len(results), chapter_id)
        return results


def _foreshadowing_to_dict(f) -> dict:
    return {
        "id": f.id,
        "novel_id": f.novel_id,
        "name": f.name,
        "description": f.description,
        "planted_at_chapter_id": f.planted_at_chapter_id,
        "payoff_at_chapter_id": f.payoff_at_chapter_id,
        "status": f.status,
        "content_snippet": f.content_snippet,
        "notes": f.notes,
        "created_at": str(f.created_at) if f.created_at else None,
        "updated_at": str(f.updated_at) if f.updated_at else None,
    }
