from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.itinerary_place import ItineraryPlace
from app.models.place import Place
from app.repositories import itinerary_place_repository as itinerary_place_repo


def get_place_recommendations(
    db: Session,
    itinerary_id: UUID,
    category: Optional[str] = None,
) -> list[Place]:
    itinerary = itinerary_place_repo.get_itinerary(db, itinerary_id)
    if itinerary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없습니다."
        )

    exclude_place_ids = itinerary_place_repo.get_existing_place_ids(db, itinerary_id)

    return itinerary_place_repo.get_recommended_places(
        db,
        region=itinerary.region,
        exclude_place_ids=exclude_place_ids,
        category=category,
    )


def add_place_to_itinerary(
    db: Session, itinerary_id: UUID, place_id: str
) -> ItineraryPlace:
    itinerary = itinerary_place_repo.get_itinerary(db, itinerary_id)
    if itinerary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없습니다."
        )

    place = itinerary_place_repo.get_place(db, place_id)
    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 장소입니다."
        )

    existing = itinerary_place_repo.get_itinerary_place_by_place_id(
        db, itinerary_id, place_id
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 담긴 장소입니다."
        )

    return itinerary_place_repo.create_itinerary_place(db, itinerary_id, place_id)


def remove_place_from_itinerary(
    db: Session, itinerary_id: UUID, itinerary_place_id: UUID
) -> None:
    itinerary_place = itinerary_place_repo.get_itinerary_place(db, itinerary_place_id)
    if itinerary_place is None or itinerary_place.itinerary_id != itinerary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="담긴 장소를 찾을 수 없습니다.",
        )

    itinerary_place_repo.delete_itinerary_place(db, itinerary_place)
