from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlaceCategory = Literal["RESTAURANT", "CAFE", "ACTIVITY"]


class PlaceDetailResponse(BaseModel):
    """
    place_id로 캐시된 장소 상세를 반환한다.
    메뉴/리뷰/평점은 자체 요약 대신 place_url(카카오맵 상세 페이지)을
    클라이언트가 웹뷰/iframe으로 열어서 보여주는 방식으로 대체한다.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    place_id: str = Field(alias="placeId")
    name: str
    category: PlaceCategory
    address: str | None = None
    lat: float
    lng: float
    place_url: str = Field(alias="placeUrl")
    thumbnail_url: str | None = Field(default=None, alias="thumbnailUrl")


# 검색 관련 스키마(PlaceSearchResponse, KakaoPlaceRaw 등)는
# /map/places/search 담당자가 자신의 구현에 맞게 이 파일에 추가하면 됨.
