"""Intent Agent — analyzes user's vague creative intent into structured directives."""

from app.services.agents.base import BaseAgent

INTENT_SYSTEM_PROMPT = """\
你是一位专业的小说编辑，负责理解作者的创作意图。

作者会用自然语言描述TA想要写的内容。你需要将模糊的意图转化为结构化的创作指令。

请返回严格 JSON 格式：
{
  "intent_type": "continuation | climax | transition | setup | payoff | character_focus | world_building",
  "plot_direction": "剧情推进方向的简短描述",
  "key_elements": ["关键要素1", "关键要素2"],
  "mood_target": "目标情绪（压抑/热血/冷幽默/温情/悲凉/紧张/恐惧/平静/愤怒/惊喜/忧伤）",
  "conflict_type": "internal | external | both | none",
  "character_focus": ["重点角色名1"],
  "world_elements": ["涉及的世界观要素"]
}

注意：
- 如果作者意图模糊，请根据上下文合理推断
- intent_type 必须从给定选项中选取
- 只返回 JSON，不要有其他文字
"""


class IntentAgent(BaseAgent):
    """Analyzes user intent and decomposes it into structured writing directives."""

    async def think(self, state: dict) -> dict:
        user_intent = state.get("user_intent", "")
        chapter_content = state.get("chapter_content", "")
        context_snippet = chapter_content[-500:] if chapter_content else ""

        if not user_intent.strip():
            return {"intent_analysis": {
                "intent_type": "continuation",
                "plot_direction": "自然延续当前剧情",
                "key_elements": [],
                "mood_target": "延续当前",
                "conflict_type": "both",
                "character_focus": [],
                "world_elements": [],
            }}

        user_prompt = f"""\
作者创作意图：
{user_intent}

当前章节末尾内容（参考上下文）：
{context_snippet}

请分析作者的创作意图并返回结构化JSON。
"""

        try:
            text = await self._call_llm(INTENT_SYSTEM_PROMPT, user_prompt)
            result = self._parse_json(text)
            return {"intent_analysis": result}
        except Exception:
            return {"intent_analysis": {"intent_type": "continuation", "plot_direction": user_intent}}
