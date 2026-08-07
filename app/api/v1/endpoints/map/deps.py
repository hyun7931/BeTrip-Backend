from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.kakao_client import KakaoMapClient, KakaoMobilityClient
from app.db.session import get_db
from app.repositories.place_repository import PlaceRepository
from app.services.place_service import PlaceService
from app.services.transit_service import TransitService


def get_place_service(db: AsyncSession = Depends(get_db)) -> PlaceService:
    return PlaceService(PlaceRepository(db), KakaoMapClient())


def get_transit_service(db: AsyncSession = Depends(get_db)) -> TransitService:
    return TransitService(PlaceRepository(db), KakaoMapClient(), KakaoMobilityClient())
