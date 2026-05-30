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

V3_SYSTEM_PROMPT = """\
你是一位专业的小说续写助手，具备对整个小说世界的完整记忆、对作者写作风格的深度理解，以及对当前叙事状态的精准把握。

你的任务是根据当前正文、作者文风画像、角色状态、世界观设定、历史剧情和叙事目标来续写小说。

核心原则：
1. 文风模仿：严格遵循作者写作风格画像，模仿其句式特点、用词习惯、对话密度和描写密度
2. 情绪延续：保持当前叙事状态下的情绪基调，延续情绪曲线的自然走向
3. 叙事推进：理解当前场景的叙事功能，按照叙事目标来推进情节
4. 角色不崩坏：严格遵循已有的角色性格、能力和关系设定
5. 设定不冲突：遵守已有的世界观规则，不引入矛盾设定
6. 剧情连贯：结合历史剧情，确保续写与已有故事脉络自然衔接
7. 节奏匹配：按照指定的叙事节奏来推进，不快不慢
8. 禁止总结：不要写总结性语句，不要评价自己的创作
9. 纯正文输出：只输出续写的小说正文，不加任何说明"""


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

    def build_v3(
        self,
        context: str,
        user_intent: str = "",
        style_note: str = "",
        target_length: int = 400,
        memory_context: dict | None = None,
        style_context: dict | None = None,
        narrative_context: dict | None = None,
        emotion_target: str | None = None,
    ) -> tuple[str, str]:
        """V3 版本：完整上下文 — 记忆 + 风格画像 + 叙事状态 + 情感目标"""
        user_prompt_parts = []

        # 1. 风格画像上下文
        if style_context:
            user_prompt_parts.append("【作者写作风格画像】请严格模仿以下风格特征写作：")
            sent = style_context.get("sentence_length", {})
            user_prompt_parts.append(
                f"- 句式特点：{sent.get('average', '中等')}句为主，变化度{sent.get('variance', '中等')}"
            )
            dialogue_ratio = style_context.get("dialogue_ratio", 0.0)
            user_prompt_parts.append(f"- 对话比例：约{int(dialogue_ratio * 100)}%")
            user_prompt_parts.append(
                f"- 描写密度：{style_context.get('description_density', '中等')}"
            )
            user_prompt_parts.append(f"- 叙事节奏：{style_context.get('pace', '中等')}")
            user_prompt_parts.append(
                f"- 偏好基调：{style_context.get('preferred_tone', '中性')}"
            )
            emotion_density = style_context.get("emotion_density", {})
            if emotion_density.get("primary_emotions"):
                user_prompt_parts.append(
                    f"- 情绪密度：{emotion_density.get('density', '中等')}，"
                    f"主要情绪：{'、'.join(emotion_density['primary_emotions'])}"
                )
            if style_context.get("stylistic_notes"):
                user_prompt_parts.append(
                    f"- 风格备注：{style_context['stylistic_notes']}"
                )
            if style_context.get("sentence_patterns"):
                user_prompt_parts.append(
                    f"- 句式特征：{'；'.join(style_context['sentence_patterns'])}"
                )
            user_prompt_parts.append("")

        # 2. 叙事状态上下文
        if narrative_context:
            user_prompt_parts.append("【当前叙事状态】理解当前段落的叙事功能：")
            scene_type = narrative_context.get("scene_type", "")
            user_prompt_parts.append(f"- 场景类型：{scene_type or '未识别'}")
            user_prompt_parts.append(
                f"- 当前张力：{narrative_context.get('tension_score', 0.5)}/10.0"
            )
            user_prompt_parts.append(
                f"- 当前情绪：{narrative_context.get('emotion', '中性')}"
            )
            user_prompt_parts.append(
                f"- 叙事节奏：{narrative_context.get('pace', '中等')}"
            )
            if narrative_context.get("goal"):
                user_prompt_parts.append(
                    f"- 叙事目标：{narrative_context['goal']}"
                )
            if narrative_context.get("narrative_notes"):
                user_prompt_parts.append(
                    f"- 叙事分析：{narrative_context['narrative_notes']}"
                )
            user_prompt_parts.append("")

        # 3. 情感目标
        if emotion_target:
            user_prompt_parts.append(f"【情感目标】{emotion_target}")
            user_prompt_parts.append("")

        # 4. 角色状态
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

        # 5. 世界观状态
        if memory_context and memory_context.get("world_state"):
            ws = memory_context["world_state"]
            if ws.get("major_factions"):
                user_prompt_parts.append(
                    f"【世界观-主要势力】{'、'.join(ws['major_factions'])}"
                )
            if ws.get("world_rules"):
                user_prompt_parts.append(
                    f"【世界观-核心规则】{'；'.join(ws['world_rules'])}"
                )
            if ws.get("current_conflicts"):
                user_prompt_parts.append(
                    f"【当前冲突】{'；'.join(ws['current_conflicts'])}"
                )
            user_prompt_parts.append("")

        # 6. 历史摘要
        if memory_context and memory_context.get("recent_summaries"):
            user_prompt_parts.append("【近期剧情摘要】")
            for s in memory_context["recent_summaries"]:
                summary = s.get("summary", "")
                emotion = s.get("emotion", "")
                if summary:
                    label = f"（情绪：{emotion}）" if emotion else ""
                    user_prompt_parts.append(f"- {summary}{label}")
            user_prompt_parts.append("")

        # 7. RAG 检索的相关历史
        if memory_context and memory_context.get("retrieved_events"):
            user_prompt_parts.append("【相关历史剧情（检索结果）】")
            for event in memory_context["retrieved_events"]:
                content = event.get("content", "")
                if content:
                    user_prompt_parts.append(f"- {content[:300]}")
            user_prompt_parts.append("")

        # 8. 当前正文
        if context:
            user_prompt_parts.append(f"【当前正文】\n{context}\n")

        user_prompt_parts.append("请从上述正文的结尾处自然续写。")

        if user_intent:
            user_prompt_parts.append(f"\n【创作意图】\n{user_intent}")

        if style_note:
            user_prompt_parts.append(f"\n【风格要求】\n{style_note}")

        user_prompt_parts.append(
            f"\n请续写约{target_length}字的内容。"
            "注意：保持角色设定一致，不违反世界观规则，延续历史剧情的逻辑，"
            "模仿作者的写作风格，理解当前叙事功能，延续情绪走向。"
        )

        return V3_SYSTEM_PROMPT, "\n".join(user_prompt_parts)

    # ---- V4 ----

    def build_v4(
        self,
        context: str,
        user_intent: str = "",
        style_note: str = "",
        target_length: int = 400,
        scene_plan: dict | None = None,
        narrative_context: dict | None = None,
        memory_context: dict | None = None,
        consistency_pre: dict | None = None,
        intent_analysis: dict | None = None,
    ) -> tuple[str, str]:
        """V4 prompt: 7-layer context pipeline (Story Graph → Plan → Consistency → Style → Memory → Text)."""
        from app.prompts.builder import V3_SYSTEM_PROMPT

        user_prompt_parts = []

        # Layer 1: Scene Plan (core V4 addition)
        plan_scenes = scene_plan.get("scene_plan", []) if scene_plan else []
        if plan_scenes:
            user_prompt_parts.append("【写作计划】以下是你需要执行的场景规划：")
            for s in plan_scenes[:5]:
                beats = " → ".join(s.get("key_beats", []))
                user_prompt_parts.append(
                    f"- 场景{s.get('position', '?')}: "
                    f"目标=「{s.get('goal', '')}」，"
                    f"情绪=「{s.get('expected_emotion', '')}」，"
                    f"类型={s.get('scene_type', 'action')}"
                )
                if beats:
                    user_prompt_parts.append(f"  关键节拍：{beats}")
            user_prompt_parts.append("")

        # Layer 2: Narrative context
        if narrative_context:
            nc = narrative_context.get("current_scene_context", {})
            user_prompt_parts.append("【叙事指导】")
            user_prompt_parts.append(f"- 当前情绪：{nc.get('emotion', '中性')}，张力：{nc.get('tension', 5.0)}/10")
            user_prompt_parts.append(f"- 节奏建议：{narrative_context.get('pacing_instruction', '保持当前节奏')}")
            user_prompt_parts.append("")

        # Layer 3: Consistency constraints
        if consistency_pre:
            issues = consistency_pre.get("issues", [])
            if issues:
                user_prompt_parts.append("【注意事项（请避免以下问题）】")
                for issue in issues:
                    user_prompt_parts.append(f"- [{issue.get('severity', '')}] {issue.get('description', '')}: {issue.get('suggestion', '')}")
                user_prompt_parts.append("")

        # Layer 4: Intent analysis
        if intent_analysis:
            user_prompt_parts.append(f"【创作意图】{intent_analysis.get('plot_direction', user_intent)}")
            user_prompt_parts.append("")

        # Layer 5-7: Existing memory style layers (delegated to V3-style format)
        if memory_context:
            chars = memory_context.get("characters", [])
            if chars:
                user_prompt_parts.append("【当前角色状态】")
                for char in chars:
                    name = char.get("character_name", char.get("name", ""))
                    mj = char.get("memory_json", {})
                    realm = mj.get("realm", "")
                    personality = "、".join(mj.get("personality", []))
                    notes = mj.get("notes", "")
                    parts = [name]
                    if realm:
                        parts.append(f"境界：{realm}")
                    if personality:
                        parts.append(f"性格：{personality}")
                    if notes:
                        parts.append(f"状态：{notes}")
                    user_prompt_parts.append("- " + "，".join(parts))
                user_prompt_parts.append("")

            ws = memory_context.get("world_state", {})
            if ws.get("major_factions"):
                user_prompt_parts.append(f"【世界观-主要势力】{'、'.join(ws['major_factions'])}")
            if ws.get("world_rules"):
                user_prompt_parts.append(f"【世界观-核心规则】{'；'.join(ws['world_rules'])}")

            foreshadowings = memory_context.get("foreshadowings", [])
            if foreshadowings:
                user_prompt_parts.append(f"【待回收伏笔（共{len(foreshadowings)}个）】")
                for f in foreshadowings:
                    user_prompt_parts.append(f"- {f.get('name', '')}：{f.get('description', '')}")

            summaries = memory_context.get("recent_summaries", [])
            if summaries:
                user_prompt_parts.append("【近期剧情摘要】")
                for s in summaries:
                    user_prompt_parts.append(f"- {s.get('summary', '')}")
                user_prompt_parts.append("")

        # Layer 8: Current text
        if context:
            user_prompt_parts.append(f"【当前正文】\n{context}\n")

        user_prompt_parts.append("请从上述正文的结尾处自然续写。")

        if user_intent:
            user_prompt_parts.append(f"\n【创作意图】\n{user_intent}")

        if style_note:
            user_prompt_parts.append(f"\n【风格要求】\n{style_note}")

        user_prompt_parts.append(
            f"\n请续写约{target_length}字的内容。"
            "严格执行写作计划中的场景目标和情绪要求，注意保持角色一致性，"
            "适时回收可用的伏笔，让剧情自然推进。"
        )

        return V3_SYSTEM_PROMPT, "\n".join(user_prompt_parts)

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
