from typing import Literal

from pydantic import BaseModel

TransitMode = Literal["CAR", "WALK"]


class TransitResponse(BaseModel):
    duration_min: int
    distance_km: float
    mode: TransitMode
