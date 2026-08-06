from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary
from app.models.itinerary_place import ItineraryPlace
from app.models.place import Place


def get_itinerary(db: Session, itinerary_id: UUID) -> Optional[Itinerary]:
    return db.get(Itinerary, itinerary_id)


def get_existing_place_ids(db: Session, itinerary_id: UUID) -> set[str]:
    """이미 이 일정에 담긴 place_id 목록 (추천 결과에서 제외할 때 사용)"""
    rows = (
        db.execute(
            select(ItineraryPlace.place_id).where(
                ItineraryPlace.itinerary_id == itinerary_id
            )
        )
        .scalars()
        .all()
    )
    return set(rows)


def get_recommended_places(
    db: Session,
    *,
    region: str,
    exclude_place_ids: set[str],
    category: Optional[str] = None,
    limit: int = 20,
) -> list[Place]:
    """region 기반 추천 후보 조회. 이미 담긴 장소는 제외.

    NOTE: places 테이블에 별도 region 컬럼이 없어 address LIKE 매칭으로
    임시 구현함. itineraries.region 값(예: '제주')과 실제 address 포맷이
    맞물리는지 확인 필요 - 안 맞으면 region 매칭 전략(좌표 반경 검색 등)을
    다시 정해야 함.
    """
    stmt = select(Place).where(Place.address.ilike(f"%{region}%"))

    if category:
        stmt = stmt.where(Place.category == category)

    if exclude_place_ids:
        stmt = stmt.where(Place.place_id.notin_(exclude_place_ids))

    stmt = stmt.limit(limit)

    return db.execute(stmt).scalars().all()


def get_place(db: Session, place_id: str) -> Optional[Place]:
    """담기 요청의 place_id가 실제 존재하는지 확인할 때 사용.
    map 도메인에 이미 place 조회 레포지토리가 있다면 그쪽 걸 재사용해도 됨."""
    return db.get(Place, place_id)


def get_itinerary_place_by_place_id(
    db: Session, itinerary_id: UUID, place_id: str
) -> Optional[ItineraryPlace]:
    """중복 담기 체크용 (uq_itinerary_places_place)"""
    return db.execute(
        select(ItineraryPlace).where(
            ItineraryPlace.itinerary_id == itinerary_id,
            ItineraryPlace.place_id == place_id,
        )
    ).scalar_one_or_none()


def create_itinerary_place(
    db: Session, itinerary_id: UUID, place_id: str
) -> ItineraryPlace:
    """day/time_slot/order_in_day는 NULL(스케줄 미배치)로 생성"""
    itinerary_place = ItineraryPlace(itinerary_id=itinerary_id, place_id=place_id)
    db.add(itinerary_place)
    db.commit()
    db.refresh(itinerary_place)
    return itinerary_place


def get_itinerary_place(
    db: Session, itinerary_place_id: UUID
) -> Optional[ItineraryPlace]:
    return db.get(ItineraryPlace, itinerary_place_id)


def delete_itinerary_place(db: Session, itinerary_place: ItineraryPlace) -> None:
    db.delete(itinerary_place)
    db.commit()
