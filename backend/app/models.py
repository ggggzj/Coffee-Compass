from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    JSON,
    REAL,
    TIMESTAMP,
    Boolean,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from app.db import Base


class Cafe(Base):
    __tablename__ = "cafes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    google_place_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float] = mapped_column(nullable=False)
    lng: Mapped[float] = mapped_column(nullable=False)
    rating: Mapped[float | None] = mapped_column(REAL, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    categories: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    opening_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    has_wifi: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_outlet: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    noise_level: Mapped[str | None] = mapped_column(String, nullable=True)
    good_for_studying: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    ambience_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    editorial_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_snippets: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("name", "version", name="prompt_versions_name_version_uq"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
