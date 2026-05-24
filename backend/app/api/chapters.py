from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chapter import ChapterCreate, ChapterListResponse, ChapterResponse, ChapterUpdate
from app.services.chapter import ChapterService

router = APIRouter(tags=["chapters"])


@router.get("/novels/{novel_id}/chapters", response_model=ChapterListResponse)
async def list_chapters(novel_id: int, db: AsyncSession = Depends(get_db)):
    service = ChapterService(db)
    chapters = await service.list_chapters(novel_id)
    return ChapterListResponse(
        chapters=[ChapterResponse.model_validate(c) for c in chapters]
    )


@router.post("/novels/{novel_id}/chapters", response_model=ChapterResponse, status_code=201)
async def create_chapter(novel_id: int, data: ChapterCreate, db: AsyncSession = Depends(get_db)):
    service = ChapterService(db)
    chapter = await service.create_chapter(novel_id, data.title)
    return ChapterResponse.model_validate(chapter)


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    service = ChapterService(db)
    chapter = await service.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return ChapterResponse.model_validate(chapter)


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(chapter_id: int, data: ChapterUpdate, db: AsyncSession = Depends(get_db)):
    service = ChapterService(db)
    update_data = data.model_dump(exclude_unset=True)
    chapter = await service.update_chapter(chapter_id, **update_data)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return ChapterResponse.model_validate(chapter)


@router.delete("/chapters/{chapter_id}", status_code=204)
async def delete_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    service = ChapterService(db)
    chapter = await service.delete_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
