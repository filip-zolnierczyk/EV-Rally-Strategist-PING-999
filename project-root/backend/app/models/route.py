from typing import Tuple
from pydantic import BaseModel

class RouteRequest(BaseModel):
    start: Tuple[float, float]
    end: Tuple[float, float]
