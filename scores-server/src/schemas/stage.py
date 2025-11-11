"""Stage schemas."""
from typing import List, Optional
from src.schemas.base import CamelCaseModel

from src.schemas.common import Division, StageType
from src.schemas.pool import Pool


class StageBase(CamelCaseModel):
    """Base stage schema."""
    name: str
    stage_type: StageType
    division: Division
    order: int = 0


class StageCreate(StageBase):
    """Schema for creating a stage."""
    id: str
    tournament_id: str


class Stage(StageBase):
    """Full stage schema."""
    id: str
    pools: List[Pool] = []
    schedule: Optional[List[dict]] = None  # List of match summaries
    

