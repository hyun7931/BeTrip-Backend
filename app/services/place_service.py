from fastapi import HTTPException, status

from app.repositories.place_repository import PlaceRepository
from app.schemas.place import PlaceDetailResponse


class PlaceService:
    """
    상세 조회만 담당한다. 카카오 재조회 API가 없으므로,
    /map/places/search 쪽에서 미리 캐시해둔 데이터만 읽는다.
    """

    def __init__(self, repo: PlaceRepository):
        self.repo = repo

    async def get_place_detail(self, place_id: str) -> PlaceDetailResponse:
        cached = await self.repo.get_by_id(place_id)
        if cached is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="캐시된 장소 정보가 없습니다. 먼저 검색을 통해 조회해주세요.",
            )
        return PlaceDetailResponse.model_validate(cached)
