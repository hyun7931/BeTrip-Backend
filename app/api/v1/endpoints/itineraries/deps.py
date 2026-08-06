from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.itinerary_repository import ItineraryRepository
from app.services.itinerary_service import ItineraryService


def get_itinerary_service(db: AsyncSession = Depends(get_db)) -> ItineraryService:
    return ItineraryService(ItineraryRepository(db))
