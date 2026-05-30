import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.narrative_state import NarrativeStateRepository

NARRATIVE_ANALYSIS_PROMPT = """你是一位专业的小说叙事分析专家。你的任务是从叙事学角度分析给定的小说章节，理解它的叙事功能和状态。

请返回严格的 JSON 对象（不要包含 markdown 标记）：

{
  "scene_type": "dialogue|action|introspection|description|transition|冲突|铺垫|爆发|收束",
  "tension_score": 0.0-10.0,
  "emotion": "压抑|紧张|热血|悲凉|温情|冷幽默|恐惧|平静|愤怒|惊喜|忧伤",
  "pace": "slow|medium|fast",
  "goal": "这一段在叙事上承担什么功能，用中文简述",
  "emotional_curve": [
    {"position": 0, "emotion": "平静", "intensity": 0.3},
    {"position": 500, "emotion": "紧张", "intensity": 0.7}
  ],
  "narrative_notes": "关于叙事结构的进一步分析，100字以内"
}

注意：
- scene_type: 从给定选项中选最接近的
- tension_score: 0=完全松弛，10=极度紧张，用小数表示
- emotion: 该章节的主导情绪
- pace: 叙事的推进速度
- goal: 该场景/段落的叙事目标
- emotional_curve: 把章节按字符位置分成若干段，标注每段起始位置的情绪和强度（0.0-1.0）
- narrative_notes: 自由文本分析

只返回 JSON，不要任何额外说明。"""


class NarrativeService:
    def __init__(self, db: AsyncSession):
        self.repo = NarrativeStateRepository(db)

    async def get_chapter_state(self, chapter_id: int) -> dict | None:
        ns = await self.repo.get_by_chapter(chapter_id)
        if not ns:
            return None
        return {
            "scene_type": ns.scene_type,
            "tension_score": ns.tension_score,
            "emotion": ns.emotion,
            "pace": ns.pace,
            "goal": ns.goal,
            "emotional_curve": ns.emotional_curve,
            "narrative_notes": ns.narrative_json.get("narrative_notes", ""),
        }

    async def list_novel_states(self, novel_id: int) -> list:
        return await self.repo.list_by_novel(novel_id)

    async def analyze_chapter(
        self,
        novel_id: int,
        chapter_id: int,
        content: str,
        llm_client,
    ) -> dict:
        if not content or not content.strip():
            return {}

        # 取章节内容用于分析（前后各取2500字符，共5000字符）
        analysis_text = content[:5000]

        try:
            output = await llm_client.complete(
                system_prompt=NARRATIVE_ANALYSIS_PROMPT,
                user_prompt=f"分析以下小说章节的叙事状态：\n\n{analysis_text}",
            )
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                data = {
                    "scene_type": result.get("scene_type"),
                    "tension_score": result.get("tension_score", 0.5),
                    "emotion": result.get("emotion"),
                    "pace": result.get("pace", "medium"),
                    "goal": result.get("goal"),
                    "emotional_curve": result.get("emotional_curve", []),
                    "narrative_json": result,
                }
                await self.repo.upsert(novel_id, chapter_id, data)
                return result
        except Exception:
            pass
        return {}
