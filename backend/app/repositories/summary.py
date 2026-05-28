from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.summary import Summary


class SummaryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_novel(self, novel_id: int, summary_type: str = "chapter") -> list[Summary]:
        result = await self.db.execute(
            select(Summary)
            .where(Summary.novel_id == novel_id, Summary.summary_type == summary_type)
            .order_by(Summary.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_chapter(self, chapter_id: int) -> Summary | None:
        result = await self.db.execute(
            select(Summary).where(Summary.chapter_id == chapter_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, summary_id: int) -> Summary | None:
        result = await self.db.execute(select(Summary).where(Summary.id == summary_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        novel_id: int,
        summary_text: str,
        summary_type: str = "chapter",
        chapter_id: int | None = None,
        characters: list | None = None,
        important_events: list | None = None,
        emotion: str | None = None,
        foreshadowing: list | None = None,
        embedding_id: str | None = None,
    ) -> Summary:
        summary = Summary(
            novel_id=novel_id,
            chapter_id=chapter_id,
            summary_type=summary_type,
            summary_text=summary_text,
            characters=characters or [],
            important_events=important_events or [],
            emotion=emotion,
            foreshadowing=foreshadowing or [],
            embedding_id=embedding_id,
        )
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)
        return summary

    async def update_embedding_id(self, summary_id: int, embedding_id: str) -> Summary | None:
        summary = await self.get_by_id(summary_id)
        if summary:
            summary.embedding_id = embedding_id
            await self.db.commit()
            await self.db.refresh(summary)
        return summary

    async def delete_by_chapter(self, chapter_id: int) -> bool:
        summary = await self.get_by_chapter(chapter_id)
        if summary:
            await self.db.delete(summary)
            await self.db.commit()
            return True
        return False
