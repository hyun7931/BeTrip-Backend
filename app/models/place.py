from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Float,
    Index,
    String,
    Text,
    func,
)

from app.db.base import Base


class Place(Base):
    """DDL: places 테이블과 1:1 매칭"""

    __tablename__ = "places"

    place_id = Column(String(50), primary_key=True)  # Kakao Place ID 그대로 사용
    name = Column(String(200), nullable=False)
    category = Column(String(20), nullable=False)
    address = Column(String(300))
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    place_url = Column(Text)  # 카카오맵 상세 페이지 (웹뷰/iframe 임베드용)
    thumbnail_url = Column(Text)  # place_url의 og:image에서 가져온 값
    source = Column(String(20), nullable=False, server_default="KAKAO")
    source_synced_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "category IN ('RESTAURANT', 'CAFE', 'ACTIVITY')",
            name="chk_places_category",
        ),
        Index("idx_places_category", "category"),
        Index("idx_places_name", "name"),
    )
