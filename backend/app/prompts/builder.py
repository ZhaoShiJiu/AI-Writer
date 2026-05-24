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
