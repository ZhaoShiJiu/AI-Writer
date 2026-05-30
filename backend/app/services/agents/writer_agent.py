"""Writer Agent — generates the final text using the complete V4 context."""

from app.services.agents.base import BaseAgent
from app.prompts.builder import PromptBuilder

V4_SYSTEM_PROMPT = """\
你是一位专业的小说创作AI，具备完整的故事智能。

你不仅会续写文字，更理解：
- **故事结构**：高潮、铺垫、转折、收束
- **角色弧光**：角色在故事中的成长和变化
- **伏笔系统**：设置和回收伏笔
- **情绪曲线**：控制读者的情绪体验
- **节奏把控**：快慢结合，张弛有度

创作规则：
1. 严格遵循写作计划中的场景目标和情绪要求
2. 保持与已有角色性格、战力、知识水平完全一致
3. 遵从世界规则，不违反已建立的设定
4. 注意伏笔的设置和回收时机
5. 文风与已有章节保持一致
6. 对话自然，描写生动，不做总结性陈述
7. 只输出纯正文，不要任何解释或标记
8. 输出长度应与目标字数接近
"""


class WriterAgent(BaseAgent):
    """Generates the final prose using the complete V4 multi-agent context."""

    def __init__(self, prompt_builder: PromptBuilder | None = None):
        super().__init__()
        self.prompt_builder = prompt_builder or PromptBuilder()

    async def think(self, state: dict) -> dict:
        chapter_content = state.get("chapter_content", "")
        user_intent = state.get("user_intent", "")
        style_note = state.get("style_note", "")
        target_length = state.get("target_length", 400)

        # Gather all context layers
        scene_plan = state.get("scene_plan", {})
        narrative_context = state.get("narrative_context", {})
        memory_context = state.get("memory_context", {})
        consistency_pre = state.get("consistency_pre", {})
        intent_analysis = state.get("intent_analysis", {})
        graph_context = state.get("graph_context", {})

        # Build V4 user prompt manually (layered approach)
        user_prompt_parts = []

        # Layer 1: Scene Plan
        plan_scenes = scene_plan.get("scene_plan", [])
        if plan_scenes:
            user_prompt_parts.append("【写作计划】")
            for s in plan_scenes[:3]:
                user_prompt_parts.append(
                    f"场景{s.get('position', '?')}: "
                    f"目标=「{s.get('goal', '')}」, "
                    f"情绪=「{s.get('expected_emotion', '')}」, "
                    f"类型={s.get('scene_type', '')}"
                )
                beats = s.get("key_beats", [])
                if beats:
                    user_prompt_parts.append(f"  关键节拍：{' → '.join(beats)}")

        # Layer 2: Narrative context
        if narrative_context:
            nc = narrative_context.get("current_scene_context", {})
            user_prompt_parts.append(f"\n【叙事指导】")
            user_prompt_parts.append(f"当前情绪：{nc.get('emotion', '中性')}，张力：{nc.get('tension', 5.0)}/10")
            user_prompt_parts.append(f"节奏建议：{narrative_context.get('pacing_instruction', '保持当前节奏')}")

        # Layer 3: Consistency constraints
        issues = consistency_pre.get("issues", [])
        if issues:
            user_prompt_parts.append(f"\n【注意事项（请避免以下问题）】")
            for issue in issues:
                user_prompt_parts.append(f"- [{issue.get('severity', '')}] {issue.get('description', '')}")

        # Layer 4: Intent analysis
        if intent_analysis:
            user_prompt_parts.append(f"\n【创作意图】{intent_analysis.get('plot_direction', '')}")

        # Layer 5: Memory context (characters, world, summaries)
        from app.services.agents.memory_agent import MemoryAgent
        mem_text = MemoryAgent.format_for_prompt(memory_context)
        if mem_text.strip():
            user_prompt_parts.append(f"\n{mem_text}")

        # Layer 6: Graph context
        if graph_context:
            graph_nodes = graph_context.get("nodes", [])
            if graph_nodes:
                char_nodes = [n for n in graph_nodes if n.get("node_type") == "character"]
                if char_nodes:
                    user_prompt_parts.append(f"\n【故事图谱-角色网络】")
                    for n in char_nodes[:10]:
                        user_prompt_parts.append(f"- {n.get('label', '')}")

        # Layer 7: Current text + intent
        context_text = ""
        if chapter_content:
            # Strip HTML and get last N chars
            import re
            clean = re.sub(r"<[^>]+>", "", chapter_content)
            context_text = clean[-2000:]

        user_prompt_parts.append(f"\n【当前正文末尾】\n{context_text}")
        user_prompt_parts.append(f"\n【创作要求】")
        user_prompt_parts.append(f"创作意图：{user_intent or '自然延续剧情'}")

        if style_note:
            user_prompt_parts.append(f"风格要求：{style_note}")
        user_prompt_parts.append(f"目标字数：约{target_length}字")

        user_prompt = "\n".join(user_prompt_parts)

        try:
            ai_output = await self._call_llm(V4_SYSTEM_PROMPT, user_prompt)
            return {"generated_text": ai_output}
        except Exception as e:
            return {"generated_text": f"[V4生成失败: {e}]"}
