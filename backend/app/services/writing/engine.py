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
from app.services.style import StyleService
from app.services.narrative import NarrativeService
from app.services.emotion import EmotionService


class WritingEngine:
    """V3 写作引擎 — 集成记忆系统 + 风格分析 + 叙事理解 + RAG 检索的续写服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.chapter_repo = ChapterRepository(db)
        self.char_service = CharacterMemoryService(db)
        self.world_service = WorldMemoryService(db)
        self.summary_generator = SummaryGenerator(db)
        self.style_service = StyleService(db)
        self.narrative_service = NarrativeService(db)
        self.emotion_service = EmotionService(db)
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

    async def generate_continuation_v3(
        self,
        chapter_id: int,
        novel_id: int,
        user_intent: str = "",
        style_note: str = "",
        target_length: int | None = None,
        emotion_target: str | None = None,
    ):
        """V3 续写：整合记忆 + 风格画像 + 叙事状态 + 情感目标"""
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

        # V3: 收集风格上下文
        style_context = await self._gather_style_context(novel_id)

        # V3: 收集叙事上下文
        narrative_context = await self._gather_narrative_context(
            novel_id=novel_id,
            chapter_id=chapter_id,
            content=chapter.content,
        )

        # V3: 收集情感目标
        if not emotion_target:
            emotion_target = await self.emotion_service.get_target_emotion_context(
                chapter_id
            )

        context = self._extract_context(chapter.content)

        system_prompt, user_prompt = self.prompt_builder.build_v3(
            context=context,
            user_intent=user_intent,
            style_note=style_note,
            target_length=target_length,
            memory_context=memory_context,
            style_context=style_context,
            narrative_context=narrative_context,
            emotion_target=emotion_target,
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

    async def _gather_style_context(self, novel_id: int) -> dict | None:
        """收集风格上下文：懒加载风格画像"""
        try:
            profile = await self.style_service.get_style_profile(novel_id)
            if not profile:
                # 首次：触发风格分析
                profile = await self.style_service.analyze_and_save(
                    novel_id, self.llm_client
                )
            return profile
        except Exception:
            return None

    async def _gather_narrative_context(
        self, novel_id: int, chapter_id: int, content: str
    ) -> dict | None:
        """收集叙事上下文：懒加载叙事状态"""
        try:
            state = await self.narrative_service.get_chapter_state(chapter_id)
            if not state:
                # 首次：触发叙事分析
                result = await self.narrative_service.analyze_chapter(
                    novel_id=novel_id,
                    chapter_id=chapter_id,
                    content=content,
                    llm_client=self.llm_client,
                )
                state = {
                    "scene_type": result.get("scene_type"),
                    "tension_score": result.get("tension_score", 0.5),
                    "emotion": result.get("emotion"),
                    "pace": result.get("pace", "medium"),
                    "goal": result.get("goal"),
                    "emotional_curve": result.get("emotional_curve", []),
                    "narrative_notes": result.get("narrative_notes", ""),
                }
            return state
        except Exception:
            return None

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

        # V3: 分析叙事状态
        try:
            await self.narrative_service.analyze_chapter(
                novel_id=novel_id,
                chapter_id=chapter_id,
                content=content,
                llm_client=self.llm_client,
            )
        except Exception:
            pass

        # V4: 同步 Neo4j 故事图谱
        try:
            from app.services.graph.story_graph import story_graph_service
            # Sync characters
            characters = await self.char_service.list_characters(novel_id)
            await story_graph_service.sync_characters(novel_id, characters)
            await story_graph_service.sync_character_relations(novel_id, characters)
            # Sync world (factions + locations)
            world_state = await self.world_service.get_world_state_dict(novel_id)
            if world_state:
                await story_graph_service.sync_factions_and_locations(novel_id, world_state)
            # Sync events from summaries
            summaries = await self.summary_generator.get_recent_summaries(novel_id, limit=10)
            await story_graph_service.sync_events(novel_id, summaries)
        except Exception:
            pass

        # V4: 检测本章伏笔
        try:
            from app.services.foreshadowing import ForeshadowingService
            foreshadowing_service = ForeshadowingService(self.db)
            detected = await foreshadowing_service.detect_from_chapter(
                novel_id=novel_id,
                chapter_id=chapter_id,
                content=content,
            )
            if detected:
                logger.info("Detected %d foreshadowings in chapter %d", len(detected), chapter_id)
        except Exception:
            pass

    async def generate_v4(
        self,
        chapter_id: int,
        novel_id: int,
        user_intent: str = "",
        style_note: str = "",
        target_length: int | None = None,
        emotion_target: str | None = None,
        pace_target: str | None = None,
        planner_input: dict | None = None,
    ) -> AIGeneration | None:
        """V4续写：LangGraph多智能体工作流"""
        from app.services.workflow.graph import get_v4_workflow
        from app.services.workflow.state import WorkflowState

        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            return None

        initial_state: WorkflowState = {
            "novel_id": novel_id,
            "chapter_id": chapter_id,
            "chapter_content": chapter.content or "",
            "user_intent": user_intent,
            "style_note": style_note,
            "target_length": target_length or settings.continuation_target_chars,
            "emotion_target": emotion_target,
            "pace_target": pace_target,
            "planner_input": planner_input or {},
            "model": "deepseek/deepseek-v4-pro",
            "_db_session": self.db,
            "_retry_count": 0,
        }

        try:
            workflow = get_v4_workflow()
            final_state = await workflow.ainvoke(initial_state)
        except Exception:
            # Fallback to V3 on workflow failure
            return await self.generate_continuation_v3(
                chapter_id, novel_id, user_intent, style_note, target_length, emotion_target
            )

        generated_text = final_state.get("rewritten_text") or final_state.get("generated_text", "")
        if not generated_text:
            return None

        generation = AIGeneration(
            chapter_id=chapter_id,
            user_intent=user_intent,
            prompt_text="V4 Multi-Agent Workflow",
            ai_output=generated_text,
        )
        self.db.add(generation)
        await self.db.commit()
        await self.db.refresh(generation)

        # Save generation context for debugging
        from app.models.generation_context import GenerationContext
        try:
            ctx = GenerationContext(
                generation_id=generation.id,
                context_json={
                    "workflow_steps": final_state.get("current_step", ""),
                    "intent_analysis": final_state.get("intent_analysis"),
                    "consistency_pre": final_state.get("consistency_pre"),
                    "consistency_post": final_state.get("consistency_post"),
                },
            )
            self.db.add(ctx)
            await self.db.commit()
        except Exception:
            pass

        return generation

    def _extract_context(self, content: str) -> str:
        content = re.sub(r"<[^>]+>", "", content)
        content = content.strip()
        if len(content) > settings.context_max_chars:
            content = content[-settings.context_max_chars:]
        return content
