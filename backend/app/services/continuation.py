import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.llm.client import LLMClient
from app.models.ai_generation import AIGeneration
from app.prompts.builder import PromptBuilder
from app.repositories.chapter import ChapterRepository


class ContinuationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chapter_repo = ChapterRepository(db)
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()

    async def generate_continuation(
        self,
        chapter_id: int,
        user_intent: str = "",
        style_note: str = "",
        target_length: int | None = None,
    ):
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

    def _extract_context(self, content: str) -> str:
        content = re.sub(r"<[^>]+>", "", content)
        content = content.strip()
        if len(content) > settings.context_max_chars:
            content = content[-settings.context_max_chars:]
        return content
