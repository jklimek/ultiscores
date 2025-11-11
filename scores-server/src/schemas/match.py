"""Match schemas."""
from typing import Optional, List, Dict
from datetime import datetime
from src.schemas.base import CamelCaseModel

from src.schemas.common import Division, MatchStatus, PersonName
from src.schemas.match_event import MatchEvent


class VenueSummary(CamelCaseModel):
    """Venue summary for match."""
    name: str
    city: str
    timezone: str


class MatchTeamState(CamelCaseModel):
    """Match team state."""
    team_id: str
    score: int = 0
    timeouts_remaining: int = 2
    spirit_score: Optional[float] = None


class MatchBroadcast(CamelCaseModel):
    """Match broadcast information."""
    stream_url: Optional[str] = None
    commentators: Optional[List[PersonName]] = None


class MatchOfficial(CamelCaseModel):
    """Match official."""
    name: PersonName
    role: str  # scorekeeper, observer, referee


class MatchStats(CamelCaseModel):
    """Match statistics."""
    breaks_by_team: Dict[str, int] = {}
    completions: Optional[Dict[str, int]] = None
    turnovers: Optional[Dict[str, int]] = None
    pulls: Optional[Dict[str, int]] = None


class MatchBase(CamelCaseModel):
    """Base match schema."""
    slug: str
    division: Division
    round: str
    start_time: str
    end_time: Optional[str] = None
    estimated_duration_minutes: int = 75
    field_id: Optional[str] = None
    field_label: Optional[str] = None
    status: MatchStatus = MatchStatus.SCHEDULED
    cap_at: Optional[int] = 15
    soft_cap_minutes: Optional[int] = 90
    hard_cap_minutes: Optional[int] = 110


class MatchCreate(MatchBase):
    """Schema for creating a match."""
    id: str
    tournament_id: str
    stage_id: Optional[str] = None
    pool_id: Optional[str] = None
    home_team_id: str
    away_team_id: str


class MatchUpdate(CamelCaseModel):
    """Schema for updating a match."""
    status: Optional[MatchStatus] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_timeouts: Optional[int] = None
    away_timeouts: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    field_id: Optional[str] = None
    field_label: Optional[str] = None


class MatchSummary(MatchBase):
    """Match summary for listings."""
    id: str
    tournament_id: str
    home: MatchTeamState
    away: MatchTeamState
    updated_at: Optional[datetime] = None
    


class Match(MatchBase):
    """Full match schema."""
    id: str
    tournament_id: str
    stage_id: Optional[str] = None
    pool_id: Optional[str] = None
    venue: Optional[VenueSummary] = None
    home: MatchTeamState
    away: MatchTeamState
    events: List[MatchEvent] = []
    stats: Optional[MatchStats] = None
    broadcast: Optional[MatchBroadcast] = None
    officials: Optional[List[MatchOfficial]] = None
    updated_at: Optional[datetime] = None
    

