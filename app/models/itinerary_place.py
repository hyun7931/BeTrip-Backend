from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class ItineraryPlace(Base):
    """DDL: itinerary_places 테이블과 1:1 매칭 ("담긴 장소" + "스케줄 아이템" 겸용)"""

    __tablename__ = "itinerary_places"

    itinerary_place_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    itinerary_id = Column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.itinerary_id", ondelete="CASCADE"),
        nullable=False,
    )
    place_id = Column(
        String(50),
        ForeignKey("places.place_id", ondelete="RESTRICT"),
        nullable=False,
    )
    # 담기(POST) 시점에는 NULL, 스케줄 배치 시 값이 채워짐
    day = Column(SmallInteger)
    time_slot = Column(String(10))
    order_in_day = Column(SmallInteger)
    start_time = Column(String(5))
    travel_time_to_next_min = Column(Integer)
    added_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "time_slot IN ('MORNING', 'LUNCH', 'EVENING')",
            name="chk_itinerary_places_time_slot",
        ),
        CheckConstraint(
            "day >= 1",
            name="chk_itinerary_places_day",
        ),
        UniqueConstraint("itinerary_id", "place_id", name="uq_itinerary_places_place"),
        Index(
            "idx_itinerary_places_order",
            "itinerary_id",
            "day",
            "time_slot",
            "order_in_day",
        ),
    )
