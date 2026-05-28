import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.character_memory import CharacterMemoryRepository


class CharacterMemoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CharacterMemoryRepository(db)

    async def get_character(self, novel_id: int, character_name: str) -> dict | None:
        cm = await self.repo.get_by_novel_and_name(novel_id, character_name)
        return cm.memory_json if cm else None

    async def list_characters(self, novel_id: int):
        return await self.repo.list_by_novel(novel_id)

    async def save_character(self, novel_id: int, character_name: str, memory_json: dict):
        return await self.repo.upsert(novel_id, character_name, memory_json)

    async def list_characters_as_dict(self, novel_id: int) -> list[dict]:
        """返回扁平化的角色列表，用于 LLM prompt 上下文"""
        characters = await self.repo.list_by_novel(novel_id)
        return [
            {"id": c.id, "name": c.character_name, **c.memory_json}
            for c in characters
        ]

    async def delete_character(self, novel_id: int, character_name: str) -> bool:
        return await self.repo.delete(novel_id, character_name)

    async def extract_and_save(
        self, novel_id: int, content: str, llm_client
    ) -> list[dict]:
        """使用 LLM 从文本中提取角色信息并保存"""
        system_prompt = """你是一位小说分析助手。从给定文本中提取所有角色及其状态信息。

返回 JSON 数组，每个角色包含：
- name: 角色名称
- realm: 当前境界/等级（如适用）
- personality: 性格特征数组
- relationships: 关系数组，每项包含 {target: 角色名, relation: 关系描述}
- notes: 当前状态备注

只返回 JSON，不要其他内容。"""

        try:
            output = await llm_client.complete(
                system_prompt=system_prompt,
                user_prompt=f"分析以下小说文本中的角色：\n\n{content[-3000:]}",
            )
            json_match = re.search(r"\[.*\]", output, re.DOTALL)
            if json_match:
                characters = json.loads(json_match.group())
                results = []
                for char in characters:
                    name = char.pop("name", "未知角色")
                    saved = await self.save_character(novel_id, name, char)
                    results.append(saved)
                return results
        except Exception:
            pass
        return []
