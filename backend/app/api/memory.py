from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.memory import (
    CharacterMemoryResponse,
    CharacterMemoryUpdate,
    MemorySnapshotResponse,
    WorldMemoryResponse,
    WorldMemoryUpdate,
)
from app.services.memory.character import CharacterMemoryService
from app.services.memory.world import WorldMemoryService

router = APIRouter(prefix="/api/memory", tags=["memory"])


def _format_char_response(cm) -> CharacterMemoryResponse:
    return CharacterMemoryResponse(
        id=cm.id,
        novel_id=cm.novel_id,
        character_name=cm.character_name,
        memory_json=cm.memory_json,
        created_at=cm.created_at,
        updated_at=cm.updated_at,
    )


# Character Memory

@router.get("/novels/{novel_id}/characters")
async def list_characters(novel_id: int, db: AsyncSession = Depends(get_db)):
    service = CharacterMemoryService(db)
    characters = await service.list_characters(novel_id)
    return {"characters": [_format_char_response(c) for c in characters]}


@router.put("/novels/{novel_id}/characters/{character_name}", response_model=CharacterMemoryResponse)
async def save_character(
    novel_id: int, character_name: str, data: CharacterMemoryUpdate, db: AsyncSession = Depends(get_db)
):
    service = CharacterMemoryService(db)
    result = await service.save_character(novel_id, character_name, data.memory_json)
    return _format_char_response(result)


@router.delete("/novels/{novel_id}/characters/{character_name}", status_code=204)
async def delete_character(novel_id: int, character_name: str, db: AsyncSession = Depends(get_db)):
    service = CharacterMemoryService(db)
    deleted = await service.delete_character(novel_id, character_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="角色不存在")


# World Memory

@router.get("/novels/{novel_id}/world")
async def get_world_state(novel_id: int, db: AsyncSession = Depends(get_db)):
    service = WorldMemoryService(db)
    state = await service.get_world_state_dict(novel_id)
    return {"world_state": state}


@router.put("/novels/{novel_id}/world")
async def save_world_state(novel_id: int, data: WorldMemoryUpdate, db: AsyncSession = Depends(get_db)):
    service = WorldMemoryService(db)
    result = await service.save_world_state(novel_id, data.world_state)
    return {"world_state": result}


# Memory Snapshot

@router.get("/novels/{novel_id}/snapshot", response_model=MemorySnapshotResponse)
async def get_memory_snapshot(novel_id: int, db: AsyncSession = Depends(get_db)):
    char_service = CharacterMemoryService(db)
    world_service = WorldMemoryService(db)

    characters = await char_service.list_characters(novel_id)
    world = await world_service.get_world_state(novel_id)

    return MemorySnapshotResponse(
        characters=characters,
        world=world,
    )
