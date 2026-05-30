from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.style_profile import StyleProfile


class StyleProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_novel(self, novel_id: int) -> StyleProfile | None:
        result = await self.db.execute(
            select(StyleProfile).where(StyleProfile.novel_id == novel_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, novel_id: int, style_json: dict) -> StyleProfile:
        existing = await self.get_by_novel(novel_id)
        if existing:
            existing.style_json = style_json
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        sp = StyleProfile(novel_id=novel_id, style_json=style_json)
        self.db.add(sp)
        await self.db.commit()
        await self.db.refresh(sp)
        return sp

    async def delete(self, novel_id: int) -> bool:
        sp = await self.get_by_novel(novel_id)
        if sp:
            await self.db.delete(sp)
            await self.db.commit()
            return True
        return False
