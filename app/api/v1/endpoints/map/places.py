from fastapi import APIRouter, Depends

from app.api.v1.endpoints.map.deps import get_place_service
from app.schemas.place import PlaceDetailResponse
from app.services.place_service import PlaceService

router = APIRouter()


@router.get(
    "/places/{place_id}",
    response_model=PlaceDetailResponse,
    response_model_by_alias=True,
    summary="장소 상세 조회",
)
async def get_place_detail(
    place_id: str,
    service: PlaceService = Depends(get_place_service),
):
    return await service.get_place_detail(place_id)
