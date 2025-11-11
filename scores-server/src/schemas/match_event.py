"""Match event schemas."""
from typing import Optional, List, Union, Literal
from datetime import datetime
from pydantic import Field

from src.schemas.base import CamelCaseModel
from src.schemas.common import TurnoverType, TimeoutType, CallType


class BaseMatchEvent(CamelCaseModel):
    """Base match event."""
    id: str
    sequence: int
    point: int
    elapsed_seconds: float
    clock_label: Optional[str] = None
    created_at: datetime
    team_id: Optional[str] = None
    summary: Optional[str] = None


class GoalEvent(BaseMatchEvent):
    """Goal event."""
    type: Literal["goal"] = "goal"
    scorer_id: str
    assister_id: Optional[str] = None
    offensive_line: List[str] = []


class TurnoverEvent(BaseMatchEvent):
    """Turnover event."""
    type: Literal["turnover"] = "turnover"
    turnover_type: TurnoverType
    caused_by_id: Optional[str] = None
    reason: Optional[str] = None


class TimeoutEvent(BaseMatchEvent):
    """Timeout event."""
    type: Literal["timeout"] = "timeout"
    timeout_type: TimeoutType


class CallEvent(BaseMatchEvent):
    """Call event (foul, travel, etc.)."""
    type: Literal["call"] = "call"
    call_type: CallType
    resolved: bool = True


class PullEvent(BaseMatchEvent):
    """Pull event."""
    type: Literal["pull"] = "pull"
    pulling_team_id: str


class PeriodEvent(BaseMatchEvent):
    """Period event (halftime, etc.)."""
    type: Literal["period"] = "period"
    label: str


# Discriminated union of all event types
MatchEvent = Union[
    GoalEvent,
    TurnoverEvent,
    TimeoutEvent,
    CallEvent,
    PullEvent,
    PeriodEvent,
]


class MatchEventCreate(CamelCaseModel):
    """Schema for creating a match event."""
    match_id: str
    type: str
    point: int
    elapsed_seconds: float
    clock_label: Optional[str] = None
    team_id: Optional[str] = None
    player_id: Optional[str] = None
    data: Optional[dict] = None
    summary: Optional[str] = None

