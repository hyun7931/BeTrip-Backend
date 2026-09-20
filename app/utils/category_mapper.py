def map_kakao_category(kakao_category_name: str) -> str:
    """
    카카오 category_name 예: '음식점 > 한식 > 고기', '카페 > 디저트카페'
    우리 DB의 places.category CHECK 제약: RESTAURANT | CAFE | ACTIVITY
    """
    if "음식점" in kakao_category_name:
        return "RESTAURANT"
    if "카페" in kakao_category_name:
        return "CAFE"
    return "ACTIVITY"


# 내부 category -> 카카오 category_group_code (카테고리 검색 API용)
# ACTIVITY는 카카오에 1:1 대응 코드가 없어 관광명소(AT4)로 근사한다 (부정확할 수 있음)
_CATEGORY_TO_KAKAO_GROUP_CODE = {
    "RESTAURANT": "FD6",
    "CAFE": "CE7",
    "ACTIVITY": "AT4",
}


def map_to_kakao_category_group_code(category: str) -> str:
    return _CATEGORY_TO_KAKAO_GROUP_CODE[category]
