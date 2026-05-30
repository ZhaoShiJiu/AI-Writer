from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.writing_plan import WritingPlan


class WritingPlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, plan_id: int) -> WritingPlan | None:
        result = await self.db.execute(select(WritingPlan).where(WritingPlan.id == plan_id))
        return result.scalar_one_or_none()

    async def list_by_novel(self, novel_id: int) -> list[WritingPlan]:
        result = await self.db.execute(
            select(WritingPlan)
            .where(WritingPlan.novel_id == novel_id)
            .order_by(desc(WritingPlan.created_at))
        )
        return list(result.scalars().all())

    async def get_latest(self, novel_id: int) -> WritingPlan | None:
        result = await self.db.execute(
            select(WritingPlan)
            .where(WritingPlan.novel_id == novel_id)
            .order_by(desc(WritingPlan.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, novel_id: int, data: dict) -> WritingPlan:
        plan = WritingPlan(novel_id=novel_id, **data)
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def delete(self, plan_id: int) -> bool:
        plan = await self.get_by_id(plan_id)
        if plan:
            await self.db.delete(plan)
            await self.db.commit()
            return True
        return False
