from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ValuationItem:
    category: str
    brand_model: str
    year: int
    condition_grade: float
    location: str
    sale_channel: str
    observed_at: datetime
    accessories_included: bool = False
