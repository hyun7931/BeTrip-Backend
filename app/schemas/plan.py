from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.itinerary import ItineraryStatus, ScheduleResponse, TimeSlot


class PlanGenerateResponse(BaseModel):
    itinerary_id: UUID
    status: ItineraryStatus
    schedule: ScheduleResponse | None


class PlanSaveResponse(BaseModel):
    itinerary_id: UUID
    status: ItineraryStatus
    saved_at: datetime


# ------------------------------------------------------------------
# 일정 저장 확정 POST /itineraries/{id}/plans/save
# ------------------------------------------------------------------
class PlanSaveItem(BaseModel):
    """PlanPage에서 자유 편집(담기/삭제/재배치)한 스케줄 항목 하나.

    저장 시점에 프론트가 들고 있는 현재 스케줄 전체를 이 형태로 보내면,
    서버가 itinerary_places 행의 배치 정보를 authoritative하게 덮어쓴다.
    """

    itinerary_place_id: UUID
    day: int = Field(ge=1)
    time_slot: TimeSlot
    order_in_day: int = Field(ge=1)
    travel_time_to_next_min: Optional[int] = None
    start_time: Optional[str] = None


class PlanSaveRequest(BaseModel):
    items: list[PlanSaveItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_no_duplicates(self) -> "PlanSaveRequest":
        ids = [item.itinerary_place_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("itinerary_place_id가 중복되었습니다.")

        slots = [(item.day, item.time_slot, item.order_in_day) for item in self.items]
        if len(slots) != len(set(slots)):
            raise ValueError(
                "같은 슬롯(day/time_slot/order_in_day)에 중복 배치된 항목이 있습니다."
            )

        return self
