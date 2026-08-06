import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ItineraryPlace(Base):
    """
    일정에 "담긴 장소"와 자동생성된 "스케줄 아이템"을 겸용하는 테이블.
    담기(11번)/자동생성(13번) API가 구현되기 전까지는 데이터가 적재되지 않는다.
    """

    __tablename__ = "itinerary_places"
    __table_args__ = (
        CheckConstraint(
            "time_slot IN ('MORNING', 'LUNCH', 'EVENING')",
            name="chk_itinerary_places_time_slot",
        ),
        CheckConstraint("day >= 1", name="chk_itinerary_places_day"),
        UniqueConstraint("itinerary_id", "place_id", name="uq_itinerary_places_place"),
    )

    itinerary_place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.itinerary_id", ondelete="CASCADE"),
        nullable=False,
    )
    place_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("places.place_id", ondelete="RESTRICT"),
        nullable=False,
    )
    day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    time_slot: Mapped[str] = mapped_column(String(10), nullable=False)
    order_in_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    travel_time_to_next_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
