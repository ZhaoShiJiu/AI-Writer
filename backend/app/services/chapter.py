from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chapter import ChapterRepository


class ChapterService:
    def __init__(self, db: AsyncSession):
        self.repo = ChapterRepository(db)

    async def list_chapters(self, novel_id: int):
        return await self.repo.list_by_novel(novel_id)

    async def get_chapter(self, chapter_id: int):
        return await self.repo.get_by_id(chapter_id)

    async def create_chapter(self, novel_id: int, title: str):
        chapters = await self.repo.list_by_novel(novel_id)
        position = len(chapters)
        return await self.repo.create(novel_id, title, position)

    async def update_chapter(self, chapter_id: int, **kwargs):
        chapter = await self.repo.get_by_id(chapter_id)
        if chapter:
            return await self.repo.update(chapter, **kwargs)
        return None

    async def delete_chapter(self, chapter_id: int):
        chapter = await self.repo.get_by_id(chapter_id)
        if chapter:
            await self.repo.delete(chapter)
        return chapter
