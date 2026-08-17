from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.itinerary import Itinerary
from app.models.itinerary_place import ItineraryPlace

if TYPE_CHECKING:
    from app.schemas.plan import PlanSaveItem


class ItineraryPlanRepository:
    """ItineraryPlanService(자동생성/저장) 전용 쓰기 로직.

    itinerary/itinerary_place 조회(find_by_id, find_places)는 ItineraryService와도
    공유되는 일반 조회라 ItineraryRepository에 그대로 둔다. 이 repo는 오직
    ItineraryPlanService만 사용하는, 생성/저장 흐름에서만 발생하는 쓰기 작업만 모은다.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply_generated_schedule(
        self,
        itinerary: Itinerary,
        status: str,
        assignments: list[tuple[ItineraryPlace, dict]],
    ) -> Itinerary:
        """일정 상태 변경 + itinerary_places 스케줄 필드 갱신을 한 트랜잭션으로 커밋."""
        itinerary.status = status
        for itinerary_place, fields in assignments:
            for key, value in fields.items():
                setattr(itinerary_place, key, value)
        await self.db.commit()
        await self.db.refresh(itinerary)
        return itinerary

    async def mark_saved(self, itinerary: Itinerary) -> Itinerary:
        itinerary.status = "SAVED"
        await self.db.commit()
        await self.db.refresh(itinerary)
        return itinerary

    async def touch(self, itinerary: Itinerary) -> Itinerary:
        """상태는 그대로 두고 updated_at만 현재 시각으로 갱신 (재저장 시각 갱신용)."""
        await self.db.execute(
            update(Itinerary)
            .where(Itinerary.itinerary_id == itinerary.itinerary_id)
            .values(updated_at=func.now())
        )
        await self.db.commit()
        await self.db.refresh(itinerary)
        return itinerary

    async def find_itinerary_places_by_ids(
        self, itinerary_id: UUID, ids: set[UUID]
    ) -> list[ItineraryPlace]:
        """plans/save 요청 바디의 itinerary_place_id들이 실제로 이 일정 소속인지
        확인할 때 사용 (소유권 검증용)."""
        if not ids:
            return []
        result = await self.db.execute(
            select(ItineraryPlace).where(
                ItineraryPlace.itinerary_id == itinerary_id,
                ItineraryPlace.itinerary_place_id.in_(ids),
            )
        )
        return list(result.scalars().all())

    async def bulk_update_schedule(self, items: list["PlanSaveItem"]) -> None:
        """PlanPage에서 확정된 최종 day/time_slot/order_in_day/travel_time_to_next_min을
        itinerary_places 행에 반영한다.

        - UNIQUE 제약 때문에 슬롯 순서를 바로 맞바꾸면 중간 UPDATE에서 충돌할 수 있음
            예: A: order 1->2, B: order 2->1을 A부터 적용하면 그 순간 B와 충돌
        - 따라서 2단계 UPDATE로 처리.
            - Postgres는 UNIQUE 제약에서 NULL을 서로 다른 값으로 취급하므로
            - 1단계: day를 NULL로 변경해 기존 제약을 임시 해제
            - 2단계: 최종 day / time_slot / order_in_day 값 반영
        """
        if not items:
            return
        ids = [item.itinerary_place_id for item in items]

        await self.db.execute(
            update(ItineraryPlace)
            .where(ItineraryPlace.itinerary_place_id.in_(ids))
            .values(day=None)
        )
        await self.db.flush()

        for item in items:
            await self.db.execute(
                update(ItineraryPlace)
                .where(ItineraryPlace.itinerary_place_id == item.itinerary_place_id)
                .values(
                    day=item.day,
                    time_slot=item.time_slot,
                    order_in_day=item.order_in_day,
                    travel_time_to_next_min=item.travel_time_to_next_min,
                    start_time=item.start_time,
                )
            )
        await self.db.commit()
