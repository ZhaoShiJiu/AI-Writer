from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.llm.client import LLMClient
from app.schemas.style import StyleProfileGenerateRequest, StyleProfileResponse
from app.services.style import StyleService

router = APIRouter(prefix="/api", tags=["style"])


@router.get("/novels/{novel_id}/style-profile", response_model=StyleProfileResponse)
async def get_style_profile(novel_id: int, db: AsyncSession = Depends(get_db)):
    """获取小说的风格画像"""
    service = StyleService(db)
    sp = await service.repo.get_by_novel(novel_id)
    if not sp:
        return StyleProfileResponse(
            id=0, novel_id=novel_id, style_json={}, updated_at=None
        )
    return StyleProfileResponse.model_validate(sp)


@router.post(
    "/novels/{novel_id}/style-profile", response_model=StyleProfileResponse
)
async def generate_style_profile(
    novel_id: int,
    data: StyleProfileGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """触发 AI 风格分析"""
    service = StyleService(db)

    # 如果已有画像且不强制，直接返回
    if not data.force:
        existing = await service.repo.get_by_novel(novel_id)
        if existing and existing.style_json:
            return StyleProfileResponse.model_validate(existing)

    llm_client = LLMClient()
    style_json = await service.analyze_and_save(novel_id, llm_client)
    sp = await service.repo.get_by_novel(novel_id)
    return StyleProfileResponse.model_validate(sp)
