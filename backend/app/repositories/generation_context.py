from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation_context import GenerationContext


class GenerationContextRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, generation_id: int | None, context_json: dict) -> GenerationContext:
        ctx = GenerationContext(generation_id=generation_id, context_json=context_json)
        self.db.add(ctx)
        await self.db.commit()
        await self.db.refresh(ctx)
        return ctx

    async def get_by_generation(self, generation_id: int) -> list[GenerationContext]:
        result = await self.db.execute(
            select(GenerationContext)
            .where(GenerationContext.generation_id == generation_id)
            .order_by(GenerationContext.created_at)
        )
        return list(result.scalars().all())
