from fastapi import HTTPException, status

from app.core.kakao_client import KakaoMapClient, KakaoMobilityClient
from app.repositories.place_repository import PlaceRepository
from app.schemas.transit import TransitMode, TransitResponse


class TransitService:
    def __init__(
        self,
        repo: PlaceRepository,
        kakao_map_client: KakaoMapClient,
        kakao_mobility_client: KakaoMobilityClient,
    ):
        self.repo = repo
        self.kakao_map_client = kakao_map_client
        self.kakao_mobility_client = kakao_mobility_client

    async def get_transit(
        self, from_place_id: str, to_place_id: str, mode: TransitMode
    ) -> TransitResponse:
        origin = await self.repo.get_by_id(from_place_id)
        destination = await self.repo.get_by_id(to_place_id)
        if origin is None or destination is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="캐시된 장소 정보가 없습니다. 먼저 검색을 통해 조회해주세요.",
            )

        if mode == "CAR":
            route = await self.kakao_mobility_client.get_driving_route(
                origin.lng, origin.lat, destination.lng, destination.lat
            )
        else:
            route = await self.kakao_map_client.get_walking_route(
                origin.lng, origin.lat, destination.lng, destination.lat
            )

        return TransitResponse(
            duration_min=round(route["duration_sec"] / 60),
            distance_km=round(route["distance_m"] / 1000, 1),
            mode=mode,
        )
