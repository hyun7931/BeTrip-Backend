from fastapi import APIRouter, Depends, Query

from app.api.v1.endpoints.map.deps import get_place_service
from app.schemas.place import PlaceCategory, PlaceSearchResponse
from app.services.place_service import PlaceService

router = APIRouter()


@router.get(
    "/search",
    response_model=PlaceSearchResponse,
    summary="지도 검색",
    description=(
        "**q 또는 category 중 하나는 반드시 있어야 함** — 둘 다 없으면 422.\n\n"
        "- `q`만 사용: 키워드 검색. 위치(x/y/radius, rect)는 선택 — "
        "있으면 주변으로 좁혀서 검색\n"
        "- `q` 없이 `category`만 사용: 카테고리 검색. 이때는 위치가 필수 — "
        "`x`+`y`+`radius` 조합 또는 `rect` 중 하나가 없으면 422\n"
        "- 검색 결과는 자동으로 `places` 테이블에 캐시되어, 이후 "
        "`GET /map/places/{place_id}`·`GET /map/transit`에서 바로 조회 가능"
    ),
)
async def search_places(
    q: str | None = Query(
        default=None, description="검색 키워드 (q 또는 category 필수)"
    ),
    x: float | None = Query(default=None, description="기준 좌표 경도"),
    y: float | None = Query(default=None, description="기준 좌표 위도"),
    radius: int | None = Query(default=None, description="반경(m). x,y와 함께 사용"),
    rect: str | None = Query(
        default=None, description="좌하x,좌하y,우상x,우상y — 지도 화면 영역 기준 검색"
    ),
    category: PlaceCategory | None = Query(
        default=None,
        description="카테고리 (q 또는 category 필수, category만 쓰면 위치 필수)",
    ),
    service: PlaceService = Depends(get_place_service),
):
    return await service.search_places(q, x, y, radius, rect, category)
