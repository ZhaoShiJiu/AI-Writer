from datetime import datetime

from pydantic import BaseModel


class CharacterState(BaseModel):
    name: str
    realm: str = ""
    personality: list[str] = []
    relationships: list[dict] = []
    notes: str = ""


class CharacterMemoryResponse(BaseModel):
    id: int
    novel_id: int
    character_name: str
    memory_json: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterMemoryUpdate(BaseModel):
    memory_json: dict


class WorldState(BaseModel):
    major_factions: list[str] = []
    world_rules: list[str] = []
    current_conflicts: list[str] = []
    locations: list[dict] = []
    notes: str = ""


class WorldMemoryResponse(BaseModel):
    id: int
    novel_id: int
    world_state: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorldMemoryUpdate(BaseModel):
    world_state: dict


class MemorySnapshotResponse(BaseModel):
    characters: list[CharacterMemoryResponse]
    world: WorldMemoryResponse | None
