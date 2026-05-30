import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chapter import ChapterRepository
from app.repositories.style_profile import StyleProfileRepository

STYLE_ANALYSIS_PROMPT = """你是一位专业的写作风格分析专家。你的任务是通过分析小说文本，提取作者的写作风格特征。

请从以下维度分析，返回严格的 JSON 对象（不要包含 markdown 标记）：

{
  "sentence_length": {
    "average": "short|medium|long",
    "variance": "high|medium|low"
  },
  "dialogue_ratio": 0.0-1.0,
  "emotion_density": {
    "primary_emotions": ["压抑", "热血", "冷幽默", "温情", "悲凉", "紧张"],
    "density": "high|medium|low"
  },
  "description_density": "high|medium|low",
  "pace": "fast|medium|slow",
  "preferred_tone": "压抑热血混合|轻松幽默|黑暗深沉|史诗宏大|温婉细腻|冷峻简洁",
  "common_expressions": ["常用表达1", "常用表达2"],
  "stylistic_notes": "对作者风格的文字描述，100字以内",
  "sentence_patterns": ["句式特征1", "句式特征2"]
}

注意：
- sentence_length.average: 根据多数句子的长度判断，中文短句通常10-30字，长句通常50字以上
- dialogue_ratio: 对话（引号内容）占总文本的比例
- emotion_density: 情绪描写（心理活动、情绪词、氛围描写）的密集程度
- description_density: 环境/外貌/动作描写的密集程度
- pace: 叙事推进速度，爽文快节奏，晋江风中等或慢节奏
- preferred_tone: 从给定选项中选最接近的

只返回 JSON，不要任何额外说明。"""


class StyleService:
    def __init__(self, db: AsyncSession):
        self.repo = StyleProfileRepository(db)
        self.chapter_repo = ChapterRepository(db)

    async def get_style_profile(self, novel_id: int) -> dict | None:
        sp = await self.repo.get_by_novel(novel_id)
        return sp.style_json if sp else None

    async def analyze_and_save(self, novel_id: int, llm_client) -> dict:
        chapters = await self.chapter_repo.list_by_novel(novel_id)
        if not chapters:
            return {}

        # 采样最多5章
        sample_chapters = self._sample_chapters(chapters, max_samples=5)
        samples_text = "\n\n---\n\n".join(
            f"[章节: {ch.title}]\n{ch.content[:2000]}"
            for ch in sample_chapters
            if ch.content
        )

        if not samples_text.strip():
            return {}

        try:
            output = await llm_client.complete(
                system_prompt=STYLE_ANALYSIS_PROMPT,
                user_prompt=f"分析以下小说章节的写作风格：\n\n{samples_text}",
            )
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                style_json = json.loads(json_match.group())
                await self.repo.upsert(novel_id, style_json)
                return style_json
        except Exception:
            pass
        return {}

    def _sample_chapters(self, chapters, max_samples: int = 5) -> list:
        if len(chapters) <= max_samples:
            return list(chapters)
        # 均匀采样：首、尾 + 中间均匀取
        indices = [0, len(chapters) - 1]
        step = max(1, (len(chapters) - 1) // (max_samples - 1))
        for i in range(1, max_samples - 1):
            idx = min(i * step, len(chapters) - 2)
            if idx not in indices:
                indices.append(idx)
        return [chapters[i] for i in sorted(indices)]
