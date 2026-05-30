from datetime import datetime

from pydantic import BaseModel


class StyleProfileResponse(BaseModel):
    id: int
    novel_id: int
    style_json: dict
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class StyleProfileGenerateRequest(BaseModel):
    force: bool = False
