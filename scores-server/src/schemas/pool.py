"""Pool schemas."""
from typing import List, Optional
from src.schemas.base import CamelCaseModel


class TeamInPool(CamelCaseModel):
    """Team in a pool with seed."""
    team_id: str
    seed: int


class StandingEntry(CamelCaseModel):
    """Team standing in a pool or tournament."""
    team_id: str
    rank: int
    wins: int
    losses: int
    points_for: int
    points_against: int
    point_diff: int
    spirit_average: Optional[float] = None
    streak: Optional[str] = None


class PoolBase(CamelCaseModel):
    """Base pool schema."""
    label: str
    teams: List[TeamInPool] = []


class PoolCreate(PoolBase):
    """Schema for creating a pool."""
    id: str
    stage_id: str


class Pool(PoolBase):
    """Full pool schema."""
    id: str
    stage_id: str  # Required by frontend
    standings: Optional[List[StandingEntry]] = None
    

