from fastapi import APIRouter, Depends, Query

from app.api.v1.endpoints.map.deps import get_transit_service
from app.schemas.transit import TransitMode, TransitResponse
from app.services.transit_service import TransitService

router = APIRouter()


@router.get("/transit", response_model=TransitResponse, summary="이동시간 계산")
async def get_transit(
    from_place_id: str = Query(alias="from", description="출발지 place_id"),
    to_place_id: str = Query(alias="to", description="도착지 place_id"),
    mode: TransitMode = Query(description="CAR 또는 WALK"),
    service: TransitService = Depends(get_transit_service),
):
    return await service.get_transit(from_place_id, to_place_id, mode)
