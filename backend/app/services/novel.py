from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.novel import NovelRepository


class NovelService:
    def __init__(self, db: AsyncSession):
        self.repo = NovelRepository(db)

    async def list_novels(self, user_id: int):
        return await self.repo.list_by_user(user_id)

    async def get_novel(self, novel_id: int):
        return await self.repo.get_by_id(novel_id)

    async def create_novel(self, title: str, user_id: int):
        return await self.repo.create(title, user_id)

    async def delete_novel(self, novel_id: int):
        novel = await self.repo.get_by_id(novel_id)
        if novel:
            await self.repo.delete(novel)
        return novel
