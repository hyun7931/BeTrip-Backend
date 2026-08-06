from app.utils.region_thumbnail import get_region_thumbnail


def test_get_region_thumbnail_returns_none_for_any_region_when_unmapped():
    assert get_region_thumbnail("제주도") is None
    assert get_region_thumbnail("전주") is None
