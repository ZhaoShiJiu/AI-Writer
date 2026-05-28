from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.world_memory import WorldMemory


class WorldMemoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_novel(self, novel_id: int) -> WorldMemory | None:
        result = await self.db.execute(
            select(WorldMemory).where(WorldMemory.novel_id == novel_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, novel_id: int, world_state: dict) -> WorldMemory:
        existing = await self.get_by_novel(novel_id)
        if existing:
            existing.world_state = world_state
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            wm = WorldMemory(novel_id=novel_id, world_state=world_state)
            self.db.add(wm)
            await self.db.commit()
            await self.db.refresh(wm)
            return wm

    async def delete(self, novel_id: int) -> bool:
        wm = await self.get_by_novel(novel_id)
        if wm:
            await self.db.delete(wm)
            await self.db.commit()
            return True
        return False
