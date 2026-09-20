from app.utils.category_mapper import map_kakao_category


def test_restaurant_category():
    assert map_kakao_category("음식점 > 한식 > 고기") == "RESTAURANT"


def test_cafe_category():
    assert map_kakao_category("카페 > 디저트카페") == "CAFE"


def test_unknown_category_falls_back_to_activity():
    assert map_kakao_category("여행 > 관광명소") == "ACTIVITY"


def test_empty_category_falls_back_to_activity():
    assert map_kakao_category("") == "ACTIVITY"
