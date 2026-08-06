from fastapi import APIRouter, Depends, Query

from app.api.v1.endpoints.map.deps import get_place_service
from app.schemas.place import PlaceCategory, PlaceSearchResponse
from app.services.place_service import PlaceService

router = APIRouter()


@router.get("/search", response_model=PlaceSearchResponse, summary="지도 검색")
async def search_places(
    q: str | None = Query(default=None, description="검색 키워드"),
    x: float | None = Query(default=None, description="기준 좌표 경도"),
    y: float | None = Query(default=None, description="기준 좌표 위도"),
    radius: int | None = Query(default=None, description="반경(m). x,y와 함께 사용"),
    rect: str | None = Query(
        default=None, description="좌하x,좌하y,우상x,우상y — 지도 화면 영역 기준 검색"
    ),
    category: PlaceCategory | None = Query(default=None, description="카테고리 코드"),
    service: PlaceService = Depends(get_place_service),
):
    return await service.search_places(q, x, y, radius, rect, category)
