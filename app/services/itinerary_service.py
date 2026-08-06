from uuid import UUID

from fastapi import HTTPException, status

from app.models.itinerary import Itinerary
from app.repositories.itinerary_repository import ItineraryRepository
from app.schemas.itinerary import (
    ItineraryConditionsRequest,
    ItineraryConditionsResponse,
    ItineraryCreateResponse,
    ItineraryDetailResponse,
    ItineraryPlaceResponse,
    ItinerarySummaryResponse,
)
from app.utils.region_thumbnail import get_region_thumbnail


class ItineraryService:
    def __init__(self, repo: ItineraryRepository):
        self.repo = repo

    async def create_itinerary(
        self, user_id: UUID, req: ItineraryConditionsRequest
    ) -> ItineraryCreateResponse:
        itinerary = Itinerary(
            user_id=user_id,
            status="DRAFT",
            region=req.region,
            start_date=req.start_date,
            end_date=req.end_date,
            arrival_time=req.arrival_time,
            departure_time=req.departure_time,
            transportation=req.transportation,
            purpose=req.purpose,
            styles=req.styles,
        )
        created = await self.repo.create(itinerary)
        return ItineraryCreateResponse(
            itinerary_id=created.itinerary_id,
            status=created.status,
            created_at=created.created_at,
        )

    async def list_itineraries(self, user_id: UUID) -> list[ItinerarySummaryResponse]:
        itineraries = await self.repo.find_all_by_user(user_id)
        return [
            ItinerarySummaryResponse(
                itinerary_id=itinerary.itinerary_id,
                title=itinerary.title,
                region=itinerary.region,
                start_date=itinerary.start_date,
                end_date=itinerary.end_date,
                status=itinerary.status,
                thumbnail_url=get_region_thumbnail(itinerary.region),
                updated_at=itinerary.updated_at,
            )
            for itinerary in itineraries
        ]

    async def get_itinerary_detail(
        self, user_id: UUID, itinerary_id: UUID
    ) -> ItineraryDetailResponse:
        itinerary = await self._get_owned_itinerary(user_id, itinerary_id)
        place_rows = await self.repo.find_places(itinerary_id)

        places = [
            ItineraryPlaceResponse(
                place_id=place.place_id,
                name=place.name,
                category=place.category,
                day=itinerary_place.day,
                time_slot=itinerary_place.time_slot,
                order_in_day=itinerary_place.order_in_day,
                lat=place.lat,
                lng=place.lng,
            )
            for itinerary_place, place in place_rows
        ]

        return ItineraryDetailResponse(
            itinerary_id=itinerary.itinerary_id,
            status=itinerary.status,
            conditions=ItineraryConditionsResponse.model_validate(itinerary),
            places=places,
            schedule=None,  # 자동생성(13번)/저장(15번) API 미구현 — 항상 null
            updated_at=itinerary.updated_at,
        )

    async def delete_itinerary(self, user_id: UUID, itinerary_id: UUID) -> None:
        itinerary = await self._get_owned_itinerary(user_id, itinerary_id)
        await self.repo.delete(itinerary)

    async def _get_owned_itinerary(
        self, user_id: UUID, itinerary_id: UUID
    ) -> Itinerary:
        itinerary = await self.repo.find_by_id(itinerary_id)
        if itinerary is None or itinerary.user_id != user_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "일정을 찾을 수 없습니다.")
        return itinerary
