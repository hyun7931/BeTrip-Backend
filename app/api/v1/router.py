from fastapi import APIRouter

from app.api.v1.endpoints import auth, itinerary_place, map
from app.api.v1.endpoints.itineraries.router import router as itineraries_router

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(map.router)
api_router.include_router(itineraries_router)
api_router.include_router(itinerary_place.router)
