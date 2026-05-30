from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.narrative import EmotionCurveResponse, EmotionCurveSummaryPoint
from app.services.emotion import EmotionService

router = APIRouter(prefix="/api", tags=["emotion"])


@router.get(
    "/novels/{novel_id}/emotion-curve",
    response_model=EmotionCurveResponse,
)
async def get_emotion_curve(
    novel_id: int, db: AsyncSession = Depends(get_db)
):
    """获取全书情绪曲线数据（用于前端可视化）"""
    service = EmotionService(db)
    curve = await service.get_emotion_curve(novel_id)
    return EmotionCurveResponse(
        novel_id=novel_id,
        curve=[EmotionCurveSummaryPoint(**point) for point in curve],
    )
