from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints.itineraries.router import router as itineraries_router
from app.api.v1.endpoints.map.router import router as map_router

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(itineraries_router)
api_router.include_router(map_router)
