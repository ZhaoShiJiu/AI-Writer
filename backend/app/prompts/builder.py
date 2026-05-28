SYSTEM_PROMPT = """\
你是一位专业的小说续写助手。你的任务是接续用户提供的小说正文，写出自然流畅的后续内容。

核心原则：
1. 文风一致：仔细揣摩原文的语言风格、句式节奏、用词习惯，续写必须与原文浑然一体
2. 情绪连续：把握原文的情绪基调，延续当前场景的氛围和张力
3. 内容自然：续写应该是情节的自然发展，不做突兀的跳跃和转折
4. 禁止总结：不要写出"综上所述""总而言之""故事到这里"等总结性语句
5. 不要评价：不要在续写中加入对情节的评价、解释或议论
6. 纯正文输出：只输出续写的小说正文，不要加任何前缀、说明或标注
7. 自然收束：不要在续写中强行结束场景，让故事自然地流动"""

V2_SYSTEM_PROMPT = """\
你是一位专业的小说续写助手，具备对整个小说世界的完整记忆。

你的任务是根据当前正文、角色状态、世界观设定和历史剧情来续写小说。

核心原则：
1. 文风一致：保持与原文一致的语言风格和叙事节奏
2. 角色不崩坏：严格遵循已有的角色性格、能力和关系设定
3. 设定不冲突：遵守已有的世界观规则，不引入矛盾设定
4. 剧情连贯：结合历史剧情，确保续写与已有故事脉络自然衔接
5. 情绪延续：保持当前场景的情绪张力和氛围
6. 自然推进：情节推进要自然合理，不突兀跳跃
7. 禁止总结：不要写总结性语句，不要评价自己的创作
8. 纯正文输出：只输出续写的小说正文，不加任何说明"""

POLISH_SYSTEM_PROMPT = """\
你是一位专业的小说文字润色助手。你的任务是对用户选中的小说段落进行文字润色，提升表达质量。

核心原则：
1. 保留原意：不改变原文的情节、对话内容、人物关系和情感走向
2. 优化表达：改善句式结构，增强语言节奏，提升文学表现力
3. 修正语病：修正不通顺的句子、重复的用词、不当的表达
4. 风格一致：润色后的文字必须与上下文风格浑然一体，不显突兀
5. 遵循指令：如果用户提供了具体的润色要求，严格按其指令执行
6. 纯文本输出：只输出润色后的完整段落，不要加任何前缀、说明或标注
7. 长度相近：润色后的文字长度应与原文基本一致，不要大幅扩写或缩写"""


class PromptBuilder:
    def build(
        self,
        context: str,
        user_intent: str = "",
        style_note: str = "",
        target_length: int = 400,
    ) -> tuple[str, str]:
        user_prompt_parts = []

        if context:
            user_prompt_parts.append(f"【已有正文】\n{context}\n")

        user_prompt_parts.append("请从上述正文的结尾处自然续写。")

        if user_intent:
            user_prompt_parts.append(f"\n【创作意图】\n{user_intent}")

        if style_note:
            user_prompt_parts.append(f"\n【风格要求】\n{style_note}")

        user_prompt_parts.append(f"\n请续写约{target_length}字的内容。要求：情节自然推进，保持当前的情绪张力，不要写总结性的结尾。")

        return SYSTEM_PROMPT, "\n".join(user_prompt_parts)

    def build_v2(
        self,
        context: str,
        user_intent: str = "",
        style_note: str = "",
        target_length: int = 400,
        memory_context: dict | None = None,
    ) -> tuple[str, str]:
        """V2 版本：包含记忆上下文的 Prompt 构建"""
        user_prompt_parts = []

        # 角色状态
        if memory_context and memory_context.get("characters"):
            user_prompt_parts.append("【当前角色状态】")
            for char in memory_context["characters"]:
                name = char.get("name", "")
                realm = char.get("realm", "")
                personality = char.get("personality", [])
                notes = char.get("notes", "")
                parts = [name]
                if realm:
                    parts.append(f"境界：{realm}")
                if personality:
                    parts.append(f"性格：{'、'.join(personality)}")
                if notes:
                    parts.append(f"备注：{notes}")
                user_prompt_parts.append("- " + "，".join(parts))
            user_prompt_parts.append("")

        # 世界观状态
        if memory_context and memory_context.get("world_state"):
            ws = memory_context["world_state"]
            if ws.get("major_factions"):
                user_prompt_parts.append(f"【世界观-主要势力】{'、'.join(ws['major_factions'])}")
            if ws.get("world_rules"):
                user_prompt_parts.append(f"【世界观-核心规则】{'；'.join(ws['world_rules'])}")
            if ws.get("current_conflicts"):
                user_prompt_parts.append(f"【当前冲突】{'；'.join(ws['current_conflicts'])}")
            user_prompt_parts.append("")

        # 历史摘要
        if memory_context and memory_context.get("recent_summaries"):
            user_prompt_parts.append("【近期剧情摘要】")
            for s in memory_context["recent_summaries"]:
                summary = s.get("summary", "")
                emotion = s.get("emotion", "")
                if summary:
                    label = f"（情绪：{emotion}）" if emotion else ""
                    user_prompt_parts.append(f"- {summary}{label}")
            user_prompt_parts.append("")

        # RAG 检索的相关历史
        if memory_context and memory_context.get("retrieved_events"):
            user_prompt_parts.append("【相关历史剧情（检索结果）】")
            for event in memory_context["retrieved_events"]:
                content = event.get("content", "")
                if content:
                    user_prompt_parts.append(f"- {content[:300]}")
            user_prompt_parts.append("")

        # 当前正文
        if context:
            user_prompt_parts.append(f"【当前正文】\n{context}\n")

        user_prompt_parts.append("请从上述正文的结尾处自然续写。")

        if user_intent:
            user_prompt_parts.append(f"\n【创作意图】\n{user_intent}")

        if style_note:
            user_prompt_parts.append(f"\n【风格要求】\n{style_note}")

        user_prompt_parts.append(f"\n请续写约{target_length}字的内容。注意：保持角色设定一致，不违反世界观规则，延续历史剧情的逻辑。")

        return V2_SYSTEM_PROMPT, "\n".join(user_prompt_parts)

    def build_polish(
        self,
        selected_text: str,
        context_before: str = "",
        context_after: str = "",
        requirement: str = "",
    ) -> tuple[str, str]:
        user_prompt_parts = []

        if context_before:
            user_prompt_parts.append(f"【上文】\n{context_before}\n")
        if context_after:
            user_prompt_parts.append(f"【下文】\n{context_after}\n")

        user_prompt_parts.append(f"【待润色段落】\n{selected_text}\n")

        user_prompt_parts.append("请对上述【待润色段落】进行润色，保持与上下文风格一致。")

        if requirement:
            user_prompt_parts.append(f"\n【润色要求】\n{requirement}")

        user_prompt_parts.append("\n只输出润色后的完整段落，不要添加任何说明文字。")

        return POLISH_SYSTEM_PROMPT, "\n".join(user_prompt_parts)
