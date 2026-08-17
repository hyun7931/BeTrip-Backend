from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from app.api.v1.endpoints.itineraries.deps import get_itinerary_plan_service
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.plan import (
    PlanGenerateResponse,
    PlanSaveRequest,
    PlanSaveResponse,
)
from app.services.itinerary_plan_service import ItineraryPlanService

router = APIRouter(prefix="/itineraries/{itinerary_id}/plans", tags=["itinerary_plans"])


@router.post(
    "/generate",
    response_model=PlanGenerateResponse,
    summary="Generate Itinerary Plan",
)
async def generate_plan(
    itinerary_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ItineraryPlanService = Depends(get_itinerary_plan_service),
):
    return await service.generate_plan(current_user.user_id, itinerary_id)


@router.post(
    "/save",
    response_model=PlanSaveResponse,
    summary="Save Itinerary Plan",
)
async def save_plan(
    itinerary_id: UUID,
    payload: Optional[PlanSaveRequest] = Body(default=None),
    current_user: User = Depends(get_current_user),
    service: ItineraryPlanService = Depends(get_itinerary_plan_service),
):
    """일정을 SAVED로 확정한다.

    payload.items가 있으면 PlanPage에서 자유 편집(담기/삭제/재배치)한
    현재 스케줄 전체를 먼저 itinerary_places에 반영한 뒤 상태를 확정한다.
    바디 없이 호출하면 상태 확정만 수행한다.
    """
    items = payload.items if payload else None
    return await service.save_plan(current_user.user_id, itinerary_id, items)
