from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character_memory import CharacterMemory


class CharacterMemoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_novel_and_name(self, novel_id: int, character_name: str) -> CharacterMemory | None:
        result = await self.db.execute(
            select(CharacterMemory).where(
                CharacterMemory.novel_id == novel_id,
                CharacterMemory.character_name == character_name,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_novel(self, novel_id: int) -> list[CharacterMemory]:
        result = await self.db.execute(
            select(CharacterMemory)
            .where(CharacterMemory.novel_id == novel_id)
            .order_by(CharacterMemory.character_name)
        )
        return list(result.scalars().all())

    async def upsert(self, novel_id: int, character_name: str, memory_json: dict) -> CharacterMemory:
        existing = await self.get_by_novel_and_name(novel_id, character_name)
        if existing:
            existing.memory_json = memory_json
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            cm = CharacterMemory(novel_id=novel_id, character_name=character_name, memory_json=memory_json)
            self.db.add(cm)
            await self.db.commit()
            await self.db.refresh(cm)
            return cm

    async def delete(self, novel_id: int, character_name: str) -> bool:
        cm = await self.get_by_novel_and_name(novel_id, character_name)
        if cm:
            await self.db.delete(cm)
            await self.db.commit()
            return True
        return False
