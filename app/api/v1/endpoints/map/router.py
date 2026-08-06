from fastapi import APIRouter

from app.api.v1.endpoints.map import places, search, transit

router = APIRouter(prefix="/map", tags=["map"])

router.include_router(places.router)
router.include_router(search.router)
router.include_router(transit.router)
