from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel


class NovelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: int) -> list[Novel]:
        result = await self.db.execute(
            select(Novel).where(Novel.user_id == user_id).order_by(Novel.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, novel_id: int) -> Novel | None:
        result = await self.db.execute(select(Novel).where(Novel.id == novel_id))
        return result.scalar_one_or_none()

    async def create(self, title: str, user_id: int) -> Novel:
        novel = Novel(title=title, user_id=user_id)
        self.db.add(novel)
        await self.db.commit()
        await self.db.refresh(novel)
        return novel

    async def delete(self, novel: Novel) -> None:
        await self.db.delete(novel)
        await self.db.commit()
