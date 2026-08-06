from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.place_repository import PlaceRepository
from app.services.place_service import PlaceService


def get_place_service(db: AsyncSession = Depends(get_db)) -> PlaceService:
    return PlaceService(PlaceRepository(db))
