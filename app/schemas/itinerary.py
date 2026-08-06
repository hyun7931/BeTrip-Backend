from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.place import PlaceCategory

ItineraryStatus = Literal["DRAFT", "GENERATED", "SAVED"]
TimeSlot = Literal["MORNING", "LUNCH", "EVENING"]
Transportation = Literal["CAR", "PUBLIC_TRANSPORT"]
Purpose = Literal["FRIEND", "FAMILY", "COUPLE", "PET", "PARENTS"]


class ItinerarySummaryResponse(BaseModel):
    itinerary_id: UUID
    title: str | None
    region: str
    start_date: date
    end_date: date
    status: ItineraryStatus
    thumbnail_url: str | None
    updated_at: datetime


class ItineraryListResponse(BaseModel):
    itineraries: list[ItinerarySummaryResponse]


class ItineraryConditionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_date: date
    end_date: date
    region: str
    arrival_time: TimeSlot
    departure_time: TimeSlot
    transportation: Transportation
    purpose: Purpose
    styles: list[str]


class ItineraryPlaceResponse(BaseModel):
    place_id: str
    name: str
    category: PlaceCategory
    day: int
    time_slot: TimeSlot
    order_in_day: int
    lat: float
    lng: float


class ScheduleItemResponse(BaseModel):
    place_id: str
    name: str
    time_slot: TimeSlot
    start_time: str | None
    order_in_day: int
    travel_time_to_next_min: int | None


class ScheduleDayResponse(BaseModel):
    day: int
    date: date
    items: list[ScheduleItemResponse]


class ScheduleResponse(BaseModel):
    days: list[ScheduleDayResponse]


class ItineraryDetailResponse(BaseModel):
    itinerary_id: UUID
    status: ItineraryStatus
    conditions: ItineraryConditionsResponse
    places: list[ItineraryPlaceResponse]
    schedule: ScheduleResponse | None
    updated_at: datetime
