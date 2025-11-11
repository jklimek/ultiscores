"""Tournament schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import field_validator, Field

from src.schemas.base import CamelCaseModel
from src.schemas.common import Division, TournamentStatus
from src.schemas.venue import Venue
from src.schemas.stage import Stage
from src.schemas.pool import StandingEntry


class TournamentOrganiser(CamelCaseModel):
    """Tournament organiser information."""
    name: str
    website: Optional[str] = None  # Changed from HttpUrl to str
    contact_email: Optional[str] = None
    
    @field_validator('website', 'contact_email', mode='before')
    @classmethod
    def validate_optional_fields(cls, v):
        """Convert empty strings to None for optional fields."""
        if v == '':
            return None
        return v


class TeamSeed(CamelCaseModel):
    """Team with seed in tournament."""
    team_id: str
    seed: int


class SpiritStanding(CamelCaseModel):
    """Spirit score standing."""
    team_id: str
    average: float


class TournamentSettings(CamelCaseModel):
    """Tournament generation settings."""
    format: str = "power_pools"  # pool, swiss, power_pools, single_elim, double_elim
    pool_count: Optional[int] = None
    teams_per_pool: Optional[int] = None
    advancement: Optional[Dict[str, Any]] = None
    rest_periods: int = 1
    match_duration_minutes: int = 75
    field_count: int = 2
    cap_at: Optional[int] = 15
    soft_cap_minutes: Optional[int] = 90
    hard_cap_minutes: Optional[int] = 110


class TournamentBase(CamelCaseModel):
    """Base tournament schema."""
    name: str
    slug: str
    division: Division
    start_date: str
    end_date: str
    status: TournamentStatus = TournamentStatus.UPCOMING
    organiser: Optional[TournamentOrganiser] = None
    settings: Optional[TournamentSettings] = None


class TournamentCreate(TournamentBase):
    """Schema for creating a tournament."""
    id: str
    season_id: str
    venue_id: str
    teams: List[TeamSeed] = []


class TournamentUpdate(CamelCaseModel):
    """Schema for updating a tournament."""
    name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[TournamentStatus] = None
    organiser: Optional[TournamentOrganiser] = None
    settings: Optional[TournamentSettings] = None


class TournamentSummary(CamelCaseModel):
    """Tournament summary for listings."""
    id: str
    slug: str
    name: str
    season: str = Field(validation_alias="season_id")  # Map season_id to season
    division: Division
    start_date: str
    end_date: str
    status: TournamentStatus
    updated_at: datetime


class Tournament(TournamentBase):
    """Full tournament schema."""
    id: str
    season: str = Field(validation_alias="season_id")  # Map season_id to season
    venue: Venue
    stages: List[Stage] = []
    teams: List[TeamSeed] = []
    standings: Optional[List[StandingEntry]] = None
    spirit_standings: Optional[List[SpiritStanding]] = None
    updated_at: datetime

