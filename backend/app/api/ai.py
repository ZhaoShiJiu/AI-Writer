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
from app.services.continuation import ContinuationService

router = APIRouter(tags=["ai"])


def _require_chapter(chapter):
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")


@router.post("/chapters/{chapter_id}/continue", response_model=ContinueResponse)
async def continue_chapter(chapter_id: int, data: ContinueRequest, db: AsyncSession = Depends(get_db)):
    chapter = await ChapterService(db).get_chapter(chapter_id)
    _require_chapter(chapter)

    service = ContinuationService(db)
    generation = await service.generate_continuation(
        chapter_id=chapter_id,
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

    service = ContinuationService(db)
    generation = await service.generate_continuation(
        chapter_id=chapter_id,
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

    service = ContinuationService(db)
    generation = await service.generate_polish(
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
    service = ContinuationService(db)
    generations = await service.get_generations(chapter_id)
    return GenerationListResponse(
        generations=[GenerationResponse.model_validate(g) for g in generations]
    )


@router.put("/generations/{generation_id}/accept", response_model=GenerationResponse)
async def accept_generation(generation_id: int, data: AcceptRequest, db: AsyncSession = Depends(get_db)):
    service = ContinuationService(db)
    gen = await service.accept_generation(generation_id, data.accepted)
    if not gen:
        raise HTTPException(status_code=404, detail="生成记录不存在")
    return GenerationResponse.model_validate(gen)
