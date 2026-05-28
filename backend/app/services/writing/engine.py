import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.llm.client import LLMClient
from app.models.ai_generation import AIGeneration
from app.prompts.builder import PromptBuilder
from app.repositories.chapter import ChapterRepository
from app.services.memory.character import CharacterMemoryService
from app.services.memory.world import WorldMemoryService
from app.services.rag.retriever import retriever
from app.services.summary import SummaryGenerator


class WritingEngine:
    """V2 写作引擎 — 集成记忆系统 + RAG 检索的续写服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.chapter_repo = ChapterRepository(db)
        self.char_service = CharacterMemoryService(db)
        self.world_service = WorldMemoryService(db)
        self.summary_generator = SummaryGenerator(db)
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()

    async def generate_continuation(
        self,
        chapter_id: int,
        novel_id: int,
        user_intent: str = "",
        style_note: str = "",
        target_length: int | None = None,
    ):
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            return None

        if target_length is None:
            target_length = settings.continuation_target_chars

        # V2: 收集记忆上下文
        memory_context = await self._gather_memory_context(
            novel_id=novel_id,
            chapter_content=chapter.content,
            chapter_title=chapter.title,
            chapter_id=chapter_id,
            user_intent=user_intent,
        )

        context = self._extract_context(chapter.content)

        system_prompt, user_prompt = self.prompt_builder.build_v2(
            context=context,
            user_intent=user_intent,
            style_note=style_note,
            target_length=target_length,
            memory_context=memory_context,
        )

        ai_output = await self.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        generation = AIGeneration(
            chapter_id=chapter_id,
            user_intent=user_intent,
            prompt_text=user_prompt,
            ai_output=ai_output,
        )
        self.db.add(generation)
        await self.db.commit()
        await self.db.refresh(generation)

        return generation

    async def generate_continuation_legacy(
        self,
        chapter_id: int,
        user_intent: str = "",
        style_note: str = "",
        target_length: int | None = None,
    ):
        """V1 兼容模式：不使用记忆系统"""
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            return None

        if target_length is None:
            target_length = settings.continuation_target_chars

        context = self._extract_context(chapter.content)

        system_prompt, user_prompt = self.prompt_builder.build(
            context=context,
            user_intent=user_intent,
            style_note=style_note,
            target_length=target_length,
        )

        ai_output = await self.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        generation = AIGeneration(
            chapter_id=chapter_id,
            user_intent=user_intent,
            prompt_text=user_prompt,
            ai_output=ai_output,
        )
        self.db.add(generation)
        await self.db.commit()
        await self.db.refresh(generation)

        return generation

    async def generate_polish(
        self,
        chapter_id: int,
        selected_text: str,
        context_before: str = "",
        context_after: str = "",
        requirement: str = "",
    ):
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            return None

        system_prompt, user_prompt = self.prompt_builder.build_polish(
            selected_text=selected_text,
            context_before=context_before,
            context_after=context_after,
            requirement=requirement,
        )

        ai_output = await self.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        generation = AIGeneration(
            chapter_id=chapter_id,
            user_intent=requirement,
            prompt_text=user_prompt,
            ai_output=ai_output,
        )
        self.db.add(generation)
        await self.db.commit()
        await self.db.refresh(generation)

        return generation

    async def get_generations(self, chapter_id: int) -> list[AIGeneration]:
        result = await self.db.execute(
            select(AIGeneration)
            .where(AIGeneration.chapter_id == chapter_id)
            .order_by(AIGeneration.created_at.desc())
            .limit(20)
        )
        return list(result.scalars().all())

    async def accept_generation(self, generation_id: int, accepted: bool = True) -> AIGeneration | None:
        result = await self.db.execute(
            select(AIGeneration).where(AIGeneration.id == generation_id)
        )
        gen = result.scalar_one_or_none()
        if gen:
            gen.accepted = accepted
            await self.db.commit()
            await self.db.refresh(gen)
        return gen

    async def _gather_memory_context(
        self,
        novel_id: int,
        chapter_content: str,
        chapter_title: str,
        chapter_id: int,
        user_intent: str,
    ) -> dict:
        """收集所有记忆上下文：角色状态 + 世界观 + 历史摘要 + RAG 检索结果"""
        memory_context = {
            "characters": [],
            "world_state": {},
            "recent_summaries": [],
            "retrieved_events": [],
        }

        try:
            memory_context["characters"] = await self.char_service.list_characters_as_dict(novel_id)
        except Exception:
            pass

        try:
            memory_context["world_state"] = await self.world_service.get_world_state_dict(novel_id)
        except Exception:
            pass

        try:
            memory_context["recent_summaries"] = await self.summary_generator.get_recent_summaries(novel_id, limit=5)
        except Exception:
            pass

        try:
            # RAG 检索：用用户意图和当前内容检索相关历史
            rag_query = f"{user_intent} {chapter_content[-500:]}"
            if rag_query.strip():
                memory_context["retrieved_events"] = await retriever.retrieve(
                    novel_id=novel_id,
                    query=rag_query,
                    top_k=5,
                )
        except Exception:
            pass

        return memory_context

    async def update_memory_after_save(
        self,
        novel_id: int,
        chapter_id: int,
        chapter_title: str,
        content: str,
    ):
        """章节保存后更新记忆系统：生成摘要、提取角色、索引向量"""
        # 生成章节摘要
        try:
            await self.summary_generator.generate_chapter_summary(
                novel_id=novel_id,
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                content=content,
                llm_client=self.llm_client,
            )
        except Exception:
            pass

        # 提取角色状态
        try:
            await self.char_service.extract_and_save(
                novel_id=novel_id,
                content=content,
                llm_client=self.llm_client,
            )
        except Exception:
            pass

        # 提取世界观
        try:
            await self.world_service.extract_and_save(
                novel_id=novel_id,
                content=content,
                llm_client=self.llm_client,
            )
        except Exception:
            pass

        # 索引到向量数据库
        try:
            from app.services.rag.chunker import novel_chunker
            chunks = novel_chunker.chunk_chapter(
                title=chapter_title,
                content=content,
                chapter_id=chapter_id,
            )
            await retriever.index_chapter(
                novel_id=novel_id,
                chapter_id=chapter_id,
                chunks=chunks,
            )
        except Exception:
            pass

    def _extract_context(self, content: str) -> str:
        content = re.sub(r"<[^>]+>", "", content)
        content = content.strip()
        if len(content) > settings.context_max_chars:
            content = content[-settings.context_max_chars:]
        return content
