from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.llm.client import LLMClient
from app.schemas.narrative import (
    NarrativeStateListResponse,
    NarrativeStateResponse,
)
from app.services.chapter import ChapterService
from app.services.narrative import NarrativeService

router = APIRouter(prefix="/api", tags=["narrative"])


@router.get(
    "/chapters/{chapter_id}/narrative-state",
    response_model=NarrativeStateResponse,
)
async def get_narrative_state(
    chapter_id: int, db: AsyncSession = Depends(get_db)
):
    """获取章节的叙事状态"""
    service = NarrativeService(db)
    ns = await service.repo.get_by_chapter(chapter_id)
    if not ns:
        return NarrativeStateResponse(
            id=0,
            novel_id=0,
            chapter_id=chapter_id,
            scene_type=None,
            tension_score=0.5,
            emotion=None,
            pace="medium",
            goal=None,
            emotional_curve=[],
            narrative_json={},
            created_at=None,
            updated_at=None,
        )
    return NarrativeStateResponse.model_validate(ns)


@router.get(
    "/novels/{novel_id}/narrative-states",
    response_model=NarrativeStateListResponse,
)
async def list_narrative_states(
    novel_id: int, db: AsyncSession = Depends(get_db)
):
    """获取小说的所有叙事状态"""
    service = NarrativeService(db)
    states = await service.list_novel_states(novel_id)
    return NarrativeStateListResponse(
        states=[NarrativeStateResponse.model_validate(s) for s in states]
    )


@router.post(
    "/chapters/{chapter_id}/narrative-state",
    response_model=NarrativeStateResponse,
)
async def analyze_narrative_state(
    chapter_id: int, db: AsyncSession = Depends(get_db)
):
    """触发 AI 叙事状态分析"""
    chapter = await ChapterService(db).get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    service = NarrativeService(db)
    llm_client = LLMClient()
    await service.analyze_chapter(
        novel_id=chapter.novel_id,
        chapter_id=chapter_id,
        content=chapter.content,
        llm_client=llm_client,
    )

    ns = await service.repo.get_by_chapter(chapter_id)
    return NarrativeStateResponse.model_validate(ns)
