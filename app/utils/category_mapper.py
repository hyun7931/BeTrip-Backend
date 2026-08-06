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
