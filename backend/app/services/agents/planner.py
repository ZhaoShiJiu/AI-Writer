"""Planner Agent — the core V4 agent. Auto-analyzes existing chapters + accepts manual input to create scene-level plans."""

from app.services.agents.base import BaseAgent

PLANNER_SYSTEM_PROMPT = """\
你是一位资深的小说策划/大纲师，负责为作者规划接下来的写作。

你的任务是：
1. 分析已有章节，提取小说类型、主题、角色弧光
2. 根据作者的意图，制定接下来5个场景的详细规划
3. 确保规划与现有剧情连贯，伏笔得到合理设置和回收

请返回严格 JSON 格式：
{
  "genre": "小说类型（玄幻/都市/科幻/历史/悬疑/武侠/言情/轻小说/其他）",
  "themes": ["主题1", "主题2"],
  "main_characters": ["主角名1", "配角名2"],
  "narrative_structure": "当前叙事结构描述（如：三幕式-第二幕上升阶段）",
  "scene_plan": [
    {
      "position": 1,
      "goal": "场景目标（如：引入新冲突）",
      "expected_emotion": "目标情绪",
      "scene_type": "action/dialogue/introspection/description/conflict/setup/payoff",
      "conflict_points": ["冲突点1"],
      "characters_involved": ["角色名1"],
      "estimated_length": 400,
      "key_beats": ["关键节拍1", "关键节拍2"]
    }
  ],
  "overall_arc_type": "rising/climax/falling/setup",
  "foreshadowing_opportunities": ["可埋设的伏笔机会"],
  "theme_notes": "主题把控建议（100字以内）"
}

注意：
- scene_plan 必须包含至少3个场景
- 每个场景的 goal 和 expected_emotion 必须明确
- expected_emotion 从以下选择：压抑/热血/冷幽默/温情/悲凉/紧张/恐惧/平静/愤怒/惊喜/忧伤/混合
- 只返回 JSON，不要有其他文字
"""

AUTO_ANALYSIS_PROMPT = """\
你是一位资深的小说分析家。请分析以下小说章节，提取小说的核心信息。

已有章节内容（每章前2000字采样）：

{chapter_samples}

请返回严格 JSON 格式：
{
  "genre": "小说类型",
  "themes": ["主题1", "主题2"],
  "main_characters": ["角色名1"],
  "narrative_structure": "叙事结构描述",
  "suggested_arcs": [
    {"type": "main", "title": "主线名称", "description": "主线描述"}
  ],
  "analysis_notes": "分析备注（100字以内）"
}
"""


class PlannerAgent(BaseAgent):
    """Core agent: auto-analyzes novel + creates scene-level writing plans."""

    async def think(self, state: dict) -> dict:
        intent_analysis = state.get("intent_analysis", {})
        memory_context = state.get("memory_context", {})
        planner_input = state.get("planner_input", {})

        # Build user prompt with all available context
        user_prompt_parts = []

        # Auto-analysis results if available
        auto_analysis = state.get("auto_analysis", {})
        if auto_analysis:
            user_prompt_parts.append(f"【小说分析】\n类型：{auto_analysis.get('genre', '未知')}")
            user_prompt_parts.append(f"主题：{'、'.join(auto_analysis.get('themes', []))}")
            user_prompt_parts.append(f"主要角色：{'、'.join(auto_analysis.get('main_characters', []))}")

        # Manual user input
        manual_genre = planner_input.get("manual_genre", "")
        manual_theme = planner_input.get("manual_theme", "")
        manual_direction = planner_input.get("manual_plot_direction", "")
        if manual_genre or manual_theme:
            user_prompt_parts.append(f"\n【作者手动输入】")
            if manual_genre:
                user_prompt_parts.append(f"类型：{manual_genre}")
            if manual_theme:
                user_prompt_parts.append(f"主题：{manual_theme}")
            if manual_direction:
                user_prompt_parts.append(f"剧情方向：{manual_direction}")

        # Intent analysis
        user_prompt_parts.append(f"\n【创作意图】\n意图类型：{intent_analysis.get('intent_type', 'continuation')}")
        user_prompt_parts.append(f"剧情方向：{intent_analysis.get('plot_direction', '')}")
        user_prompt_parts.append(f"目标情绪：{intent_analysis.get('mood_target', '')}")

        # Memory context summary
        chars = memory_context.get("characters", [])
        if chars:
            char_names = [c.get("character_name", c.get("name", "")) for c in chars]
            user_prompt_parts.append(f"\n【已有角色】{'、'.join(char_names)}")

        foreshadowings = memory_context.get("foreshadowings", [])
        if foreshadowings:
            f_names = [f.get("name", "") for f in foreshadowings]
            user_prompt_parts.append(f"【待回收伏笔】{'、'.join(f_names)}")

        user_prompt = "\n".join(user_prompt_parts)

        try:
            text = await self._call_llm(PLANNER_SYSTEM_PROMPT, user_prompt)
            result = self._parse_json(text)
            return {"scene_plan": result}
        except Exception:
            return {"scene_plan": {}}

    async def auto_analyze(self, chapter_samples: list[dict]) -> dict:
        """Analyze existing chapters to extract genre, themes, characters."""
        sample_texts = []
        for ch in chapter_samples:
            content = ch.get("content", "")[:2000]
            sample_texts.append(f"[章节：{ch.get('title', '')}]\n{content}")

        samples = "\n\n---\n\n".join(sample_texts) if sample_texts else "（无已有章节）"
        user_prompt = f"""\
你是一位资深的小说分析家。请分析以下小说章节，提取小说的核心信息。

已有章节内容（每章前2000字采样）：

{samples}

请返回严格 JSON 格式：
{{
  "genre": "小说类型",
  "themes": ["主题1", "主题2"],
  "main_characters": ["角色名1"],
  "narrative_structure": "叙事结构描述",
  "suggested_arcs": [
    {{"type": "main", "title": "主线名称", "description": "主线描述"}}
  ],
  "analysis_notes": "分析备注（100字以内）"
}}
"""

        try:
            text = await self._call_llm(PLANNER_SYSTEM_PROMPT, user_prompt)
            return self._parse_json(text)
        except Exception:
            return {}
