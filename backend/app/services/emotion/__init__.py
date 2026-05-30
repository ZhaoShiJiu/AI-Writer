from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chapter import ChapterRepository
from app.repositories.narrative_state import NarrativeStateRepository


class EmotionService:
    """从 NarrativeState 记录中推导情绪曲线，本身不产生新的 LLM 调用"""

    def __init__(self, db: AsyncSession):
        self.ns_repo = NarrativeStateRepository(db)
        self.chapter_repo = ChapterRepository(db)

    async def get_emotion_curve(self, novel_id: int) -> list[dict]:
        """获取全书情绪曲线数据，用于前端可视化"""
        states = await self.ns_repo.list_by_novel(novel_id)
        chapters = await self.chapter_repo.list_by_novel(novel_id)
        chapter_map = {ch.id: ch for ch in chapters}

        curve = []
        for ns in states:
            ch = chapter_map.get(ns.chapter_id)
            curve.append({
                "chapter_id": ns.chapter_id,
                "chapter_title": ch.title if ch else "未知章节",
                "chapter_position": ch.position if ch else 0,
                "emotion": ns.emotion,
                "tension_score": ns.tension_score,
            })

        # 按章节位置排序
        curve.sort(key=lambda x: x["chapter_position"])
        return curve

    async def get_target_emotion_context(self, chapter_id: int) -> str | None:
        """获取当前章节的前一章节情绪，用于续写时的情感目标"""
        current_state = await self.ns_repo.get_by_chapter(chapter_id)
        if current_state and current_state.emotion:
            return (
                f"延续'{current_state.emotion}'情绪，"
                f"当前张力{current_state.tension_score}，"
                f"节奏{current_state.pace}"
            )
        return None
