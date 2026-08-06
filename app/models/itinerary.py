from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class Itinerary(Base):
    """DDL: itineraries 테이블과 1:1 매칭"""

    __tablename__ = "itineraries"

    itinerary_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(100))
    status = Column(String(20), nullable=False, server_default="DRAFT")
    region = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    arrival_time = Column(String(10), nullable=False)
    departure_time = Column(String(10), nullable=False)
    transportation = Column(String(20), nullable=False)
    purpose = Column(String(20), nullable=False)
    styles = Column(JSONB, nullable=False, server_default="[]")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'GENERATED', 'SAVED')",
            name="chk_itineraries_status",
        ),
        CheckConstraint(
            "arrival_time IN ('MORNING', 'LUNCH', 'EVENING')",
            name="chk_itineraries_arrival_time",
        ),
        CheckConstraint(
            "departure_time IN ('MORNING', 'LUNCH', 'EVENING')",
            name="chk_itineraries_departure_time",
        ),
        CheckConstraint(
            "transportation IN ('CAR', 'PUBLIC_TRANSPORT')",
            name="chk_itineraries_transportation",
        ),
        CheckConstraint(
            "purpose IN ('FRIEND', 'FAMILY', 'COUPLE', 'PET', 'PARENTS')",
            name="chk_itineraries_purpose",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="chk_itineraries_dates",
        ),
        Index("idx_itineraries_user_updated", "user_id", updated_at.desc()),
    )
