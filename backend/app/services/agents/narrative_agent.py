"""Narrative Agent — builds on V3 NarrativeService to add arc-level planning."""

from app.services.agents.base import BaseAgent

NARRATIVE_SYSTEM_PROMPT = """\
你是一位专业的叙事分析师，负责评估当前叙事的张力、节奏和情绪状态。

请根据当前小说状态和场景计划，分析叙事态势并给出指导建议。

返回严格 JSON 格式：
{
  "current_scene_context": {
    "scene_type": "当前场景类型",
    "tension": 5.0,
    "emotion": "当前主导情绪",
    "pace": "slow/medium/fast",
    "goal": "当前叙事目标"
  },
  "emotional_curve_target": {
    "direction": "rising/falling/steady/peak/valley",
    "target_emotion": "目标情绪",
    "transition_speed": "slow/medium/fast"
  },
  "pacing_instruction": "节奏建议（如：快节奏动作描写，短句为主）",
  "narrative_notes": "叙事注意事项（100字以内）"
}
"""


class NarrativeAgent(BaseAgent):
    """Analyzes narrative state and determines how the current scene should be written."""

    async def think(self, state: dict) -> dict:
        scene_plan = state.get("scene_plan", {})
        narrative_states = state.get("_narrative_states", [])
        emotion_target = state.get("emotion_target", "")
        pace_target = state.get("pace_target", "")

        user_prompt_parts = []

        # Scene plan context
        plan_scenes = scene_plan.get("scene_plan", [])
        if plan_scenes:
            user_prompt_parts.append("【当前场景计划】")
            for s in plan_scenes[:3]:
                user_prompt_parts.append(
                    f"场景{s.get('position', '?')}: 类型={s.get('scene_type', '')}, "
                    f"目标={s.get('goal', '')}, 情绪={s.get('expected_emotion', '')}"
                )

        # Historical narrative states
        if narrative_states:
            user_prompt_parts.append("\n【历史叙事状态】")
            for ns in narrative_states[-5:]:
                user_prompt_parts.append(
                    f"章节{ns.get('chapter_id', '?')}: 场景={ns.get('scene_type', '')}, "
                    f"张力={ns.get('tension_score', 0.5)}, 情绪={ns.get('emotion', '')}"
                )

        # User targets
        if emotion_target:
            user_prompt_parts.append(f"\n【情绪目标】{emotion_target}")
        if pace_target:
            user_prompt_parts.append(f"【节奏目标】{pace_target}")

        user_prompt = "\n".join(user_prompt_parts) if user_prompt_parts else "（自动分析当前叙事态势）"

        try:
            text = await self._call_llm(NARRATIVE_SYSTEM_PROMPT, user_prompt)
            result = self._parse_json(text)
            return {"narrative_context": result}
        except Exception:
            return {"narrative_context": {
                "current_scene_context": {"scene_type": "continuation", "tension": 5.0,
                                          "emotion": "中性", "pace": "medium", "goal": "自然延续"},
                "emotional_curve_target": {"direction": "steady", "target_emotion": "延续当前", "transition_speed": "medium"},
                "pacing_instruction": "保持当前节奏",
            }}
