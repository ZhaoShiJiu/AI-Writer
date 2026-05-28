import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.summary import SummaryRepository


class SummaryGenerator:
    """章节摘要生成器 — V2 叙事记忆系统的核心组件"""

    def __init__(self, db: AsyncSession):
        self.repo = SummaryRepository(db)

    async def generate_chapter_summary(
        self,
        novel_id: int,
        chapter_id: int,
        chapter_title: str,
        content: str,
        llm_client,
    ) -> dict:
        """使用 LLM 生成章节摘要"""
        system_prompt = """你是一位专业的小说分析助手。请为以下章节内容生成结构化摘要。

返回 JSON 格式：
{
  "summary": "章节内容摘要（200字以内）",
  "characters": ["角色名1", "角色名2"],
  "important_events": ["事件1", "事件2"],
  "emotion": "整体情绪基调",
  "foreshadowing": ["伏笔1（如有）"]
}

只返回 JSON，不要其他内容。"""

        # 截取章节内容的前4000字用于分析
        text = content[:4000] if len(content) > 4000 else content
        user_prompt = f"章节标题：{chapter_title}\n\n章节内容：\n{text}"

        try:
            output = await llm_client.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return await self._save_summary(
                    novel_id=novel_id,
                    chapter_id=chapter_id,
                    data=data,
                )
        except Exception:
            pass

        # Fallback: generate simple summary
        return await self._save_summary(
            novel_id=novel_id,
            chapter_id=chapter_id,
            data={
                "summary": content[:200] + "..." if len(content) > 200 else content,
                "characters": [],
                "important_events": [],
                "emotion": "中性",
                "foreshadowing": [],
            },
        )

    async def generate_novel_summary(
        self,
        novel_id: int,
        llm_client,
    ) -> dict:
        """生成全书摘要 — 基于已有章节摘要的层级压缩"""
        chapter_summaries = await self.repo.list_by_novel(novel_id, "chapter")

        if not chapter_summaries:
            return {}

        summaries_text = "\n".join(
            f"第{i+1}章：{s.summary_text}"
            for i, s in enumerate(chapter_summaries)
        )

        system_prompt = """你是一位专业的小说分析助手。请根据各章节摘要，生成全书摘要。

返回 JSON 格式：
{
  "summary": "全书内容概述（500字以内）",
  "characters": ["所有重要角色"],
  "important_events": ["全书重要事件"],
  "emotion": "整体基调",
  "foreshadowing": ["已揭示的伏笔"]
}

只返回 JSON，不要其他内容。"""

        try:
            output = await llm_client.complete(
                system_prompt=system_prompt,
                user_prompt=f"章节摘要汇总：\n{summaries_text}",
            )
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return await self._save_summary(
                    novel_id=novel_id,
                    chapter_id=None,
                    summary_type="novel",
                    data=data,
                )
        except Exception:
            pass
        return {}

    async def _save_summary(
        self,
        novel_id: int,
        chapter_id: int | None,
        data: dict,
        summary_type: str = "chapter",
    ) -> dict:
        """保存摘要到数据库，如果已存在则更新"""
        if chapter_id:
            existing = await self.repo.get_by_chapter(chapter_id)
            if existing:
                await self.repo.delete_by_chapter(chapter_id)

        summary = await self.repo.create(
            novel_id=novel_id,
            chapter_id=chapter_id,
            summary_type=summary_type,
            summary_text=data.get("summary", ""),
            characters=data.get("characters", []),
            important_events=data.get("important_events", []),
            emotion=data.get("emotion"),
            foreshadowing=data.get("foreshadowing", []),
        )

        return {
            "id": summary.id,
            "summary": summary.summary_text,
            "characters": summary.characters,
            "important_events": summary.important_events,
            "emotion": summary.emotion,
            "foreshadowing": summary.foreshadowing,
        }

    async def get_chapter_summary(self, chapter_id: int) -> dict | None:
        """获取已生成的章节摘要"""
        summary = await self.repo.get_by_chapter(chapter_id)
        if not summary:
            return None
        return {
            "id": summary.id,
            "summary": summary.summary_text,
            "characters": summary.characters,
            "important_events": summary.important_events,
            "emotion": summary.emotion,
            "foreshadowing": summary.foreshadowing,
        }

    async def get_recent_summaries(
        self, novel_id: int, limit: int = 5
    ) -> list[dict]:
        """获取最近的摘要列表"""
        summaries = await self.repo.list_by_novel(novel_id, "chapter")
        return [
            {
                "id": s.id,
                "chapter_id": s.chapter_id,
                "summary": s.summary_text,
                "characters": s.characters,
                "important_events": s.important_events,
                "emotion": s.emotion,
                "foreshadowing": s.foreshadowing,
            }
            for s in summaries[:limit]
        ]
