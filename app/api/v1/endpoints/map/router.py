from fastapi import APIRouter

from app.api.v1.endpoints.map import places

router = APIRouter(prefix="/map", tags=["map"])

router.include_router(places.router)
# 나중에 지도 검색, 경로 등이 추가되면 여기서만 include_router 추가하면 됨
