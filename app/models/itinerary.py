import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Itinerary(Base):
    __tablename__ = "itineraries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'GENERATED', 'SAVED')", name="chk_itineraries_status"
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
        CheckConstraint("end_date >= start_date", name="chk_itineraries_dates"),
    )

    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    region: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    arrival_time: Mapped[str] = mapped_column(String(10), nullable=False)
    departure_time: Mapped[str] = mapped_column(String(10), nullable=False)
    transportation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(20), nullable=True)
    styles: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
