"""
일정 목록 카드에 쓸 지역 대표 이미지 매핑.
실제 이미지 에셋이 정해지지 않아 비워둔 상태 — 값이 채워지면 매핑만 추가하면 됨.
"""

REGION_THUMBNAILS: dict[str, str] = {}


def get_region_thumbnail(region: str) -> str | None:
    return REGION_THUMBNAILS.get(region)
