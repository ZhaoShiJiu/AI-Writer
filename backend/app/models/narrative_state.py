from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NarrativeState(Base):
    __tablename__ = "narrative_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    scene_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tension_score: Mapped[float] = mapped_column(Float, default=0.5)
    emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pace: Mapped[str] = mapped_column(String(50), default="medium")
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotional_curve: Mapped[list] = mapped_column(JSONB, default=list)
    narrative_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
