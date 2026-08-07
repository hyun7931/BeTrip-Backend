from fastapi import APIRouter

from app.api.v1.endpoints.itineraries import itineraries, plans

router = APIRouter()

router.include_router(itineraries.router)
router.include_router(plans.router)
