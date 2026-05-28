from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    summary_type: Mapped[str] = mapped_column(String(50), nullable=False, default="chapter")
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    characters: Mapped[list] = mapped_column(JSONB, default=list)
    important_events: Mapped[list] = mapped_column(JSONB, default=list)
    emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    foreshadowing: Mapped[list] = mapped_column(JSONB, default=list)
    embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
