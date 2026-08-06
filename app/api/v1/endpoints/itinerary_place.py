from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db  # 실제 프로젝트 경로에 맞게 수정 필요
from app.schemas.itinerary_place_schema import (
    ItineraryPlaceCreateRequest,
    ItineraryPlaceResponse,
    PlaceCategory,
    PlaceRecommendResponse,
)
from app.services import itinerary_place_service

router = APIRouter(
    prefix="/itineraries/{itinerary_id}/places", tags=["itinerary_places"]
)


@router.get("/recommend", response_model=PlaceRecommendResponse)
def recommend_places(
    itinerary_id: UUID,
    category: Optional[PlaceCategory] = Query(default=None),
    db: Session = Depends(get_db),
) -> PlaceRecommendResponse:
    """지역/목적/스타일 기반으로 아직 담기지 않은 장소를 추천한다."""
    places = itinerary_place_service.get_place_recommendations(
        db, itinerary_id, category=category
    )
    return PlaceRecommendResponse(places=places)


@router.post(
    "",
    response_model=ItineraryPlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_place(
    itinerary_id: UUID,
    payload: ItineraryPlaceCreateRequest,
    db: Session = Depends(get_db),
) -> ItineraryPlaceResponse:
    """일정에 장소를 담는다. day/time_slot/order_in_day는 아직 NULL(미배치)."""
    return itinerary_place_service.add_place_to_itinerary(
        db, itinerary_id, payload.place_id
    )


@router.delete(
    "/{itinerary_place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_place(
    itinerary_id: UUID,
    itinerary_place_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """itinerary_place_id 기준으로 담긴 장소를 제거한다."""
    itinerary_place_service.remove_place_from_itinerary(
        db, itinerary_id, itinerary_place_id
    )
