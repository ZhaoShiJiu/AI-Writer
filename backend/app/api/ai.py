from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ai import (
    AcceptRequest,
    ContinueRequest,
    ContinueResponse,
    GenerationListResponse,
    GenerationResponse,
    PolishRequest,
    PolishResponse,
    RegenerateRequest,
)
from app.services.chapter import ChapterService
from app.services.writing.engine import WritingEngine

router = APIRouter(tags=["ai"])


def _require_chapter(chapter):
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")


@router.post("/chapters/{chapter_id}/continue", response_model=ContinueResponse)
async def continue_chapter(chapter_id: int, data: ContinueRequest, db: AsyncSession = Depends(get_db)):
    chapter = await ChapterService(db).get_chapter(chapter_id)
    _require_chapter(chapter)

    engine = WritingEngine(db)
    generation = await engine.generate_continuation(
        chapter_id=chapter_id,
        novel_id=chapter.novel_id,
        user_intent=data.user_intent,
        style_note=data.style_note,
        target_length=data.target_length,
    )

    return ContinueResponse(
        generation_id=generation.id,
        ai_output=generation.ai_output,
    )


@router.post("/chapters/{chapter_id}/regenerate", response_model=ContinueResponse)
async def regenerate_chapter(chapter_id: int, data: RegenerateRequest, db: AsyncSession = Depends(get_db)):
    chapter = await ChapterService(db).get_chapter(chapter_id)
    _require_chapter(chapter)

    engine = WritingEngine(db)
    generation = await engine.generate_continuation(
        chapter_id=chapter_id,
        novel_id=chapter.novel_id,
        user_intent=data.user_intent,
        style_note=data.style_note,
    )

    return ContinueResponse(
        generation_id=generation.id,
        ai_output=generation.ai_output,
    )


@router.post("/chapters/{chapter_id}/polish", response_model=PolishResponse)
async def polish_chapter(chapter_id: int, data: PolishRequest, db: AsyncSession = Depends(get_db)):
    chapter = await ChapterService(db).get_chapter(chapter_id)
    _require_chapter(chapter)

    engine = WritingEngine(db)
    generation = await engine.generate_polish(
        chapter_id=chapter_id,
        selected_text=data.selected_text,
        context_before=data.context_before,
        context_after=data.context_after,
        requirement=data.requirement,
    )

    return PolishResponse(
        generation_id=generation.id,
        polished_output=generation.ai_output,
    )


@router.get("/chapters/{chapter_id}/generations", response_model=GenerationListResponse)
async def list_generations(chapter_id: int, db: AsyncSession = Depends(get_db)):
    engine = WritingEngine(db)
    generations = await engine.get_generations(chapter_id)
    return GenerationListResponse(
        generations=[GenerationResponse.model_validate(g) for g in generations]
    )


@router.put("/generations/{generation_id}/accept", response_model=GenerationResponse)
async def accept_generation(generation_id: int, data: AcceptRequest, db: AsyncSession = Depends(get_db)):
    engine = WritingEngine(db)
    gen = await engine.accept_generation(generation_id, data.accepted)
    if not gen:
        raise HTTPException(status_code=404, detail="生成记录不存在")
    return GenerationResponse.model_validate(gen)


# V2: 记忆更新端点

@router.post("/chapters/{chapter_id}/update-memory")
async def update_chapter_memory(chapter_id: int, db: AsyncSession = Depends(get_db)):
    """章节保存后手动触发记忆更新"""
    chapter = await ChapterService(db).get_chapter(chapter_id)
    _require_chapter(chapter)

    engine = WritingEngine(db)
    await engine.update_memory_after_save(
        novel_id=chapter.novel_id,
        chapter_id=chapter_id,
        chapter_title=chapter.title,
        content=chapter.content,
    )

    return {"status": "ok", "message": "记忆已更新"}
