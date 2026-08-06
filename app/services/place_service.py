import asyncio

from fastapi import HTTPException, status

from app.core.kakao_client import KakaoMapClient
from app.core.og_preview_fetcher import fetch_og_image
from app.repositories.place_repository import PlaceRepository
from app.schemas.place import (
    PlaceCategory,
    PlaceDetailResponse,
    PlaceSearchResponse,
    PlaceSearchResult,
)
from app.utils.category_mapper import map_to_kakao_category_group_code


class PlaceService:
    def __init__(self, repo: PlaceRepository, kakao_client: KakaoMapClient):
        self.repo = repo
        self.kakao_client = kakao_client

    async def get_place_detail(self, place_id: str) -> PlaceDetailResponse:
        """
        상세 조회. 카카오 재조회 API가 없으므로 search_places가 미리 캐시해둔
        데이터만 읽는다.
        """
        cached = await self.repo.get_by_id(place_id)
        if cached is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="캐시된 장소 정보가 없습니다. 먼저 검색을 통해 조회해주세요.",
            )
        return PlaceDetailResponse.model_validate(cached)

    async def search_places(
        self,
        q: str | None,
        x: float | None,
        y: float | None,
        radius: int | None,
        rect: str | None,
        category: PlaceCategory | None,
    ) -> PlaceSearchResponse:
        category_group_code = (
            map_to_kakao_category_group_code(category) if category else None
        )

        if q:
            raw_places = await self.kakao_client.search_by_keyword(
                q,
                x=x,
                y=y,
                radius=radius,
                rect=rect,
                category_group_code=category_group_code,
            )
        elif category:
            if not rect and not (
                x is not None and y is not None and radius is not None
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="위치 정보(x/y/radius 또는 rect)가 필요합니다",
                )
            raw_places = await self.kakao_client.search_by_category(
                category_group_code, x=x, y=y, radius=radius, rect=rect
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="q 또는 category 중 하나는 필요합니다.",
            )

        thumbnails = await asyncio.gather(
            *(fetch_og_image(place.place_url) for place in raw_places)
        )

        await self.repo.upsert_many(
            [
                {
                    "place_id": place.place_id,
                    "name": place.name,
                    "category": place.category,
                    "address": place.address,
                    "lat": place.lat,
                    "lng": place.lng,
                    "place_url": place.place_url,
                    "thumbnail_url": thumbnail,
                }
                for place, thumbnail in zip(raw_places, thumbnails, strict=True)
            ]
        )

        return PlaceSearchResponse(
            places=[
                PlaceSearchResult(
                    place_id=place.place_id,
                    name=place.name,
                    category=place.category,
                    address=place.address,
                    lat=place.lat,
                    lng=place.lng,
                    thumbnail_url=thumbnail,
                )
                for place, thumbnail in zip(raw_places, thumbnails, strict=True)
            ]
        )
