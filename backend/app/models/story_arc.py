from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StoryArc(Base):
    __tablename__ = "story_arcs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    arc_type: Mapped[str] = mapped_column(String(50), nullable=False, default="main")  # main / sub / character
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_chapter_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    end_chapter_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="planned")  # planned / active / completed
    emotional_target: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pacing_plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    scene_plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
