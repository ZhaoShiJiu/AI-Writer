"""Memory Agent — gathers all memory context (characters, world, summaries, RAG, foreshadowings)."""

from app.services.agents.base import BaseAgent
from app.services.memory.character import CharacterMemoryService
from app.services.memory.world import WorldMemoryService
from app.services.summary import SummaryGenerator
from app.services.rag.retriever import retriever


class MemoryAgent(BaseAgent):
    """Gathers and compresses all memory context for the writing workflow."""

    async def think(self, state: dict) -> dict:
        novel_id = state.get("novel_id")
        chapter_id = state.get("chapter_id")
        chapter_content = state.get("chapter_content", "")
        user_intent = state.get("user_intent", "")

        if not novel_id:
            return {"memory_context": {}}

        # We need a DB session — but agents are stateless. We create services
        # that use their own sessions. In the workflow, the db session is
        # injected from the workflow node function.

        # For now, return a placeholder; the actual memory gathering happens
        # in the workflow node (which has DB session access).
        # The MemoryAgent provides the logic to format gathered data.

        return {"memory_context": state.get("_raw_memory", {})}

    @staticmethod
    def format_for_prompt(memory_context: dict) -> str:
        """Format memory context dict into a prompt string."""
        parts = []

        chars = memory_context.get("characters", [])
        if chars:
            parts.append("【当前角色状态】")
            for c in chars:
                name = c.get("character_name", c.get("name", ""))
                mj = c.get("memory_json", {})
                realm = mj.get("realm", "")
                personality = "、".join(mj.get("personality", []))
                notes = mj.get("notes", "")
                line = f"- {name}"
                if realm:
                    line += f"（境界：{realm}）"
                if personality:
                    line += f" 性格：{personality}"
                if notes:
                    line += f" 状态：{notes}"
                parts.append(line)

        world = memory_context.get("world_state", {})
        if world:
            parts.append("\n【世界观状态】")
            factions = world.get("major_factions", [])
            if factions:
                parts.append(f"主要势力：{'、'.join(factions)}")
            rules = world.get("world_rules", [])
            if rules:
                parts.append(f"世界规则：{'；'.join(rules)}")
            conflicts = world.get("current_conflicts", [])
            if conflicts:
                parts.append(f"当前冲突：{'；'.join(conflicts)}")

        summaries = memory_context.get("recent_summaries", [])
        if summaries:
            parts.append("\n【近期剧情摘要】")
            for s in summaries:
                parts.append(f"- {s.get('summary', '')}")

        rag_events = memory_context.get("rag_events", [])
        if rag_events:
            parts.append("\n【相关历史剧情】")
            for evt in rag_events:
                parts.append(f"- {evt}")

        foreshadowings = memory_context.get("foreshadowings", [])
        if foreshadowings:
            parts.append("\n【待回收伏笔】")
            for f in foreshadowings:
                parts.append(f"- {f.get('name', '')}：{f.get('description', '')}")

        return "\n".join(parts)
