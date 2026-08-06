from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.place import Place


class PlaceRepository:
    """
    place_id로 캐시된 장소를 읽는 것만 담당한다.
    검색 결과를 캐시에 적재(upsert)하는 로직은 /map/places/search 담당자가
    이 파일에 자신의 메서드를 추가하는 방식으로 구현하면 된다.
    (여기서 upsert 방식을 미리 정해두지 않음 — 담당자가 자기 방식대로 설계)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, place_id: str) -> Place | None:
        result = await self.db.execute(select(Place).where(Place.place_id == place_id))
        return result.scalar_one_or_none()
