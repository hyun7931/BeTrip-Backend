import httpx
from core.config import get_settings
from fastapi import HTTPException, status
from schemas.place import KakaoPlaceRaw
from utils.category_mapper import map_kakao_category

settings = get_settings()

KEYWORD_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


class KakaoMapClient:
    """
    카카오 로컬 API는 place_id로 단건 상세를 주는 엔드포인트가 없다.
    키워드/카테고리 검색 결과 안에서만 place_id, place_url을 얻을 수 있다.
    그래서 이 클라이언트는 '검색'만 제공하고, 검색 결과를 places 테이블에
    캐시해두는 방식으로 설계한다. (place_id 단건 재조회 API는 존재하지 않음)
    """

    def __init__(self):
        self._headers = {"Authorization": f"KakaoAK {settings.kakao_rest_api_key}"}

    async def search_by_keyword(
        self, query: str, page: int = 1, size: int = 15
    ) -> list[KakaoPlaceRaw]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(
                    KEYWORD_SEARCH_URL,
                    params={"query": query, "page": page, "size": size},
                    headers=self._headers,
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"카카오맵 API 오류: {e.response.status_code}",
                ) from e
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="카카오맵 API 연결 실패",
                ) from e

            data = resp.json()
            return [self._parse(doc) for doc in data.get("documents", [])]

    def _parse(self, doc: dict) -> KakaoPlaceRaw:
        return KakaoPlaceRaw(
            place_id=doc["id"],
            name=doc["place_name"],
            category=map_kakao_category(doc.get("category_name", "")),
            address=doc.get("road_address_name") or doc.get("address_name"),
            lat=float(doc["y"]),
            lng=float(doc["x"]),
            place_url=doc["place_url"],
        )
