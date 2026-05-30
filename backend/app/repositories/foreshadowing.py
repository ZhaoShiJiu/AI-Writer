from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.foreshadowing import Foreshadowing


class ForeshadowingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, fid: int) -> Foreshadowing | None:
        result = await self.db.execute(select(Foreshadowing).where(Foreshadowing.id == fid))
        return result.scalar_one_or_none()

    async def list_by_novel(self, novel_id: int) -> list[Foreshadowing]:
        result = await self.db.execute(
            select(Foreshadowing)
            .where(Foreshadowing.novel_id == novel_id)
            .order_by(Foreshadowing.created_at)
        )
        return list(result.scalars().all())

    async def list_pending(self, novel_id: int) -> list[Foreshadowing]:
        """伏笔状态为 planted 或 reminded 的（未回收的）"""
        result = await self.db.execute(
            select(Foreshadowing)
            .where(
                Foreshadowing.novel_id == novel_id,
                Foreshadowing.status.in_(["planted", "reminded"]),
            )
            .order_by(Foreshadowing.created_at)
        )
        return list(result.scalars().all())

    async def create(self, novel_id: int, data: dict) -> Foreshadowing:
        f = Foreshadowing(novel_id=novel_id, **data)
        self.db.add(f)
        await self.db.commit()
        await self.db.refresh(f)
        return f

    async def update(self, fid: int, data: dict) -> Foreshadowing | None:
        f = await self.get_by_id(fid)
        if f:
            for key, value in data.items():
                setattr(f, key, value)
            await self.db.commit()
            await self.db.refresh(f)
        return f

    async def delete(self, fid: int) -> bool:
        f = await self.get_by_id(fid)
        if f:
            await self.db.delete(f)
            await self.db.commit()
            return True
        return False
