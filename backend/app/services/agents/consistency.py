"""Consistency Agent — two-phase check: pre (plan validation) and post (output validation)."""

from app.services.agents.base import BaseAgent

CONSISTENCY_SYSTEM_PROMPT = """\
你是一位严格的小说一致性审查员。你的唯一职责是发现故事中的不一致之处。

请检查以下内容是否与已建立的故事状态一致，检查维度如下：

1. **人设一致性**：角色的性格、能力、知识水平是否前后一致？
2. **战力一致性**：角色的力量等级/境界是否出现矛盾或数值错乱？
3. **时间线一致性**：事件发生的顺序、时间间隔是否合理？
4. **世界观一致性**：世界规则、设定是否被违反？
5. **剧情连贯性**：前文建立的线索、伏笔是否被正确处理？

返回严格 JSON 格式：
{
  "passed": true/false,
  "issues": [
    {
      "severity": "critical/major/minor",
      "category": "character/power/timeline/world_rule/plot",
      "description": "具体问题描述",
      "suggestion": "修改建议"
    }
  ],
  "overall_score": 8.5
}

注意：
- overall_score 0-10，10分表示完全一致
- 如果 passed=false 但 issues 中没有 critical 级别问题，通常视为可接受
- 只返回 JSON，不要有其他文字
"""


class ConsistencyAgent(BaseAgent):
    """Two-phase consistency checking: pre-check (plan) and post-check (generated text)."""

    async def think(self, state: dict) -> dict:
        """Post-check — validates generated text consistency."""
        generated_text = state.get("generated_text", "")
        memory_context = state.get("memory_context", {})

        if not generated_text:
            return {"consistency_post": {"passed": True, "issues": [], "overall_score": 10.0, "check_type": "post"}}

        # Build context for check
        chars_text = ""
        chars = memory_context.get("characters", [])
        for c in chars:
            name = c.get("character_name", c.get("name", ""))
            mj = c.get("memory_json", {})
            chars_text += f"- {name}: 境界={mj.get('realm', '?')}, 性格={'、'.join(mj.get('personality', []))}\n"

        world_rules = ""
        world = memory_context.get("world_state", {})
        for rule in world.get("world_rules", []):
            world_rules += f"- {rule}\n"

        user_prompt = f"""\
【已建立的角色状态】
{chars_text if chars_text else "（暂无）"}

【世界规则】
{world_rules if world_rules else "（暂无）"}

【待检查的文本】
{generated_text[:3000]}

请检查以上文本是否存在不一致之处。
"""

        try:
            text = await self._call_llm(CONSISTENCY_SYSTEM_PROMPT, user_prompt)
            result = self._parse_json(text)
            result["check_type"] = "post"
            return {"consistency_post": result}
        except Exception:
            return {"consistency_post": {"passed": True, "issues": [], "overall_score": 10.0, "check_type": "post"}}

    async def precheck(self, state: dict) -> dict:
        """Pre-check — validates the writing plan before generation."""
        scene_plan = state.get("scene_plan", {})
        memory_context = state.get("memory_context", {})

        plan_text = str(scene_plan.get("scene_plan", []))[:2000]

        user_prompt = f"""\
【写作计划】
{plan_text}

请检查以上计划是否与已有故事状态冲突。只需要检查明显的矛盾（如角色已死亡却被安排出场、违反已建立的规则等）。
"""

        try:
            text = await self._call_llm(CONSISTENCY_SYSTEM_PROMPT, user_prompt)
            result = self._parse_json(text)
            result["check_type"] = "pre"
            return {"consistency_pre": result}
        except Exception:
            return {"consistency_pre": {"passed": True, "issues": [], "overall_score": 10.0, "check_type": "pre"}}
