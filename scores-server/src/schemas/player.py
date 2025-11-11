"""Player schemas."""
from typing import Optional, List
from datetime import date
from pydantic import field_validator

from src.schemas.base import CamelCaseModel
from src.schemas.common import Division, PersonName


class PlayerTeamHistory(CamelCaseModel):
    """Player team history entry."""
    team_id: str
    team_name: str
    season: str
    division: Division
    tournaments: List[dict] = []  # [{tournamentId, tournamentName, placement}]


class PlayerBase(CamelCaseModel):
    """Base player schema."""
    first_name: str
    last_name: str
    pronouns: Optional[str] = None
    nationality: Optional[str] = "POL"
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = None
    throws: Optional[str] = None  # left, right, both
    roles: List[str] = []  # ["handler", "cutter", "flex"]
    dominant_positions: List[str] = []
    profile_image_url: Optional[str] = None  # Changed from HttpUrl
    
    @field_validator('profile_image_url', mode='before')
    @classmethod
    def validate_url(cls, v):
        """Convert empty strings to None."""
        if v == '':
            return None
        return v


class PlayerCreate(PlayerBase):
    """Schema for creating a player."""
    id: str


class PlayerUpdate(CamelCaseModel):
    """Schema for updating a player."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    pronouns: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = None
    throws: Optional[str] = None
    roles: Optional[List[str]] = None
    dominant_positions: Optional[List[str]] = None
    profile_image_url: Optional[str] = None


class PlayerStats(CamelCaseModel):
    """Player statistics summary."""
    total_goals: int = 0
    total_assists: int = 0
    total_ds: int = 0
    total_points_played: int = 0


class Player(PlayerBase):
    """Full player schema."""
    id: str
    jersey_number: Optional[int] = None
    name: PersonName
    club_history: List[PlayerTeamHistory] = []
    stats: Optional[PlayerStats] = None

