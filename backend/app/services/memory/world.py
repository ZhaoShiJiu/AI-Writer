from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.world_memory import WorldMemoryRepository


class WorldMemoryService:
    def __init__(self, db: AsyncSession):
        self.repo = WorldMemoryRepository(db)

    async def get_world_state(self, novel_id: int):
        return await self.repo.get_by_novel(novel_id)

    async def get_world_state_dict(self, novel_id: int) -> dict:
        wm = await self.repo.get_by_novel(novel_id)
        return wm.world_state if wm else {}

    async def save_world_state(self, novel_id: int, world_state: dict) -> dict:
        wm = await self.repo.upsert(novel_id, world_state)
        return wm.world_state

    async def update_world_field(self, novel_id: int, field: str, value) -> dict:
        current = await self.get_world_state_dict(novel_id)
        current[field] = value
        return await self.save_world_state(novel_id, current)

    async def delete_world_state(self, novel_id: int) -> bool:
        return await self.repo.delete(novel_id)

    async def extract_and_save(
        self, novel_id: int, content: str, llm_client
    ) -> dict:
        """使用 LLM 从文本中提取世界观信息并保存"""
        system_prompt = """你是一位小说分析助手。从给定文本中提取世界观设定。

返回 JSON 对象：
- major_factions: 主要势力/组织列表
- world_rules: 世界观规则/设定列表
- current_conflicts: 当前冲突列表
- locations: 重要地点列表，每项包含 {name: 名称, description: 描述}
- notes: 其他备注

只返回 JSON，不要其他内容。"""

        try:
            import json
            import re

            output = await llm_client.complete(
                system_prompt=system_prompt,
                user_prompt=f"分析以下小说文本中的世界观设定：\n\n{content[-4000:]}",
            )
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                world_state = json.loads(json_match.group())
                return await self.save_world_state(novel_id, world_state)
        except Exception:
            pass
        return await self.get_world_state_dict(novel_id)
