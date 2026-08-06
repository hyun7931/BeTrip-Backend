from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

TimeSlot = Literal["MORNING", "LUNCH", "EVENING"]
PlaceCategory = Literal["RESTAURANT", "CAFE", "ACTIVITY"]


# ------------------------------------------------------------------
# 장소 추천 GET /itineraries/{iId}/places/recommend
# ------------------------------------------------------------------
class RecommendedPlace(BaseModel):
    """places 테이블 기반 추천 결과 아이템"""

    model_config = ConfigDict(from_attributes=True)

    place_id: str
    name: str
    category: PlaceCategory
    address: Optional[str] = None
    lat: float
    lng: float
    thumbnail_url: Optional[str] = None


class PlaceRecommendResponse(BaseModel):
    places: list[RecommendedPlace]


# ------------------------------------------------------------------
# 장소 담기 POST /itineraries/{iId}/places
# ------------------------------------------------------------------
class ItineraryPlaceCreateRequest(BaseModel):
    """담기 시점에는 place_id만 받는다.

    day/time_slot/order_in_day는 아직 스케줄 미배치 상태(NULL)로 생성되고,
    이후 별도 스케줄 배치 기능에서 채워진다.
    """

    place_id: str


class ItineraryPlaceResponse(BaseModel):
    """itinerary_places 테이블과 1:1 매칭되는 응답.

    day/time_slot/order_in_day는 스케줄 미배치 상태면 null로 내려간다.
    """

    model_config = ConfigDict(from_attributes=True)

    itinerary_place_id: UUID
    itinerary_id: UUID
    place_id: str
    day: Optional[int] = None
    time_slot: Optional[TimeSlot] = None
    order_in_day: Optional[int] = None
    start_time: Optional[str] = None
    travel_time_to_next_min: Optional[int] = None
    added_at: datetime
    updated_at: datetime


# ------------------------------------------------------------------
# 장소 제거 DELETE /itineraries/{iId}/places/{itineraryPlaceId}
# ------------------------------------------------------------------
# 응답 바디 없이 204 No Content로 처리 (별도 스키마 불필요)
