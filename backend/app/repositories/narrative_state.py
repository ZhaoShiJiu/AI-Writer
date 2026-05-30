from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.narrative_state import NarrativeState


class NarrativeStateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_chapter(self, chapter_id: int) -> NarrativeState | None:
        result = await self.db.execute(
            select(NarrativeState).where(NarrativeState.chapter_id == chapter_id)
        )
        return result.scalar_one_or_none()

    async def list_by_novel(self, novel_id: int) -> list[NarrativeState]:
        result = await self.db.execute(
            select(NarrativeState)
            .where(NarrativeState.novel_id == novel_id)
            .order_by(NarrativeState.created_at.asc())
        )
        return list(result.scalars().all())

    async def upsert(
        self, novel_id: int, chapter_id: int, data: dict
    ) -> NarrativeState:
        existing = await self.get_by_chapter(chapter_id)
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        ns = NarrativeState(novel_id=novel_id, chapter_id=chapter_id, **data)
        self.db.add(ns)
        await self.db.commit()
        await self.db.refresh(ns)
        return ns

    async def delete_by_chapter(self, chapter_id: int) -> bool:
        ns = await self.get_by_chapter(chapter_id)
        if ns:
            await self.db.delete(ns)
            await self.db.commit()
            return True
        return False
