from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.novel import NovelCreate, NovelListResponse, NovelResponse
from app.services.novel import NovelService

router = APIRouter(tags=["novels"])

DEFAULT_USER_ID = 1


@router.get("/novels", response_model=NovelListResponse)
async def list_novels(db: AsyncSession = Depends(get_db)):
    service = NovelService(db)
    novels = await service.list_novels(DEFAULT_USER_ID)
    return NovelListResponse(novels=[NovelResponse.model_validate(n) for n in novels])


@router.post("/novels", response_model=NovelResponse, status_code=201)
async def create_novel(data: NovelCreate, db: AsyncSession = Depends(get_db)):
    service = NovelService(db)
    novel = await service.create_novel(data.title, DEFAULT_USER_ID)
    return NovelResponse.model_validate(novel)


@router.get("/novels/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: int, db: AsyncSession = Depends(get_db)):
    service = NovelService(db)
    novel = await service.get_novel(novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")
    return NovelResponse.model_validate(novel)


@router.delete("/novels/{novel_id}", status_code=204)
async def delete_novel(novel_id: int, db: AsyncSession = Depends(get_db)):
    service = NovelService(db)
    novel = await service.delete_novel(novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")
