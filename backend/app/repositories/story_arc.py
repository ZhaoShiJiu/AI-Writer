from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story_arc import StoryArc


class StoryArcRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, arc_id: int) -> StoryArc | None:
        result = await self.db.execute(select(StoryArc).where(StoryArc.id == arc_id))
        return result.scalar_one_or_none()

    async def list_by_novel(self, novel_id: int) -> list[StoryArc]:
        result = await self.db.execute(
            select(StoryArc)
            .where(StoryArc.novel_id == novel_id)
            .order_by(StoryArc.created_at)
        )
        return list(result.scalars().all())

    async def create(self, novel_id: int, data: dict) -> StoryArc:
        arc = StoryArc(novel_id=novel_id, **data)
        self.db.add(arc)
        await self.db.commit()
        await self.db.refresh(arc)
        return arc

    async def update(self, arc_id: int, data: dict) -> StoryArc | None:
        arc = await self.get_by_id(arc_id)
        if arc:
            for key, value in data.items():
                setattr(arc, key, value)
            await self.db.commit()
            await self.db.refresh(arc)
        return arc

    async def delete(self, arc_id: int) -> bool:
        arc = await self.get_by_id(arc_id)
        if arc:
            await self.db.delete(arc)
            await self.db.commit()
            return True
        return False
