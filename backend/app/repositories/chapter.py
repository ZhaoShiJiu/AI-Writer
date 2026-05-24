from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chapter import Chapter


class ChapterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_novel(self, novel_id: int) -> list[Chapter]:
        result = await self.db.execute(
            select(Chapter)
            .where(Chapter.novel_id == novel_id)
            .order_by(Chapter.position)
        )
        return list(result.scalars().all())

    async def get_by_id(self, chapter_id: int) -> Chapter | None:
        result = await self.db.execute(select(Chapter).where(Chapter.id == chapter_id))
        return result.scalar_one_or_none()

    async def create(self, novel_id: int, title: str, position: int) -> Chapter:
        chapter = Chapter(novel_id=novel_id, title=title, position=position)
        self.db.add(chapter)
        await self.db.commit()
        await self.db.refresh(chapter)
        return chapter

    async def update(self, chapter: Chapter, **kwargs) -> Chapter:
        for key, value in kwargs.items():
            if value is not None:
                setattr(chapter, key, value)
        await self.db.commit()
        await self.db.refresh(chapter)
        return chapter

    async def delete(self, chapter: Chapter) -> None:
        await self.db.delete(chapter)
        await self.db.commit()
