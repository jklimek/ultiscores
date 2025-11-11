"""Common schemas used across models."""
from enum import Enum
from src.schemas.base import CamelCaseModel


class Division(str, Enum):
    """Tournament/team division."""
    OPEN = "open"
    WOMEN = "women"
    MIXED = "mixed"
    JUNIOR = "junior"
    MASTERS = "masters"


class TournamentStatus(str, Enum):
    """Tournament status."""
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StageType(str, Enum):
    """Tournament stage type."""
    ROUND_ROBIN = "round_robin"
    POOL = "pool"
    BRACKET = "bracket"
    PLACEMENT = "placement"
    RELEGATION = "relegation"
    SWISS = "swiss"


class MatchStatus(str, Enum):
    """Match status."""
    SCHEDULED = "scheduled"
    LIVE = "live"
    HALFTIME = "halftime"
    FINAL = "final"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class TurnoverType(str, Enum):
    """Type of turnover."""
    THROWAWAY = "throwaway"
    DROP = "drop"
    STALL = "stall"
    CALLAHAN = "callahan"
    BLOCK = "block"
    UNKNOWN = "unknown"


class TimeoutType(str, Enum):
    """Type of timeout."""
    TEAM = "team"
    OFFICIAL = "official"
    SPIRIT = "spirit"


class CallType(str, Enum):
    """Type of call."""
    FOUL = "foul"
    TRAVEL = "travel"
    PICK = "pick"
    INJURY = "injury"
    OTHER = "other"


class PersonName(CamelCaseModel):
    """Person name structure."""
    first: str
    last: str
    display: str

