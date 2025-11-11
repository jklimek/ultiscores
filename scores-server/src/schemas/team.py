"""Team schemas."""
from typing import Optional, List
from pydantic import field_validator

from src.schemas.base import CamelCaseModel
from src.schemas.common import Division


class TeamSeasonSummary(CamelCaseModel):
    """Team season summary."""
    season: str
    division: Division
    tournaments: List[dict] = []  # [{tournamentId, tournamentName, placement, wins, losses}]


class RosterEntry(CamelCaseModel):
    """Roster entry with player info."""
    tournament_id: str
    player: dict  # Will be populated with Player schema
    jersey_number: Optional[int] = None
    captain: bool = False


class TeamBase(CamelCaseModel):
    """Base team schema."""
    name: str
    short_name: str
    slug: str
    division: Division
    club_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Poland"
    founded_year: Optional[int] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    crest_url: Optional[str] = None  # Changed from HttpUrl
    website: Optional[str] = None  # Changed from HttpUrl
    
    @field_validator('crest_url', 'website', mode='before')
    @classmethod
    def validate_urls(cls, v):
        """Convert empty strings to None."""
        if v == '':
            return None
        return v


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    id: str


class TeamUpdate(CamelCaseModel):
    """Schema for updating a team."""
    name: Optional[str] = None
    short_name: Optional[str] = None
    club_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    founded_year: Optional[int] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    crest_url: Optional[str] = None
    website: Optional[str] = None


class Team(TeamBase):
    """Full team schema."""
    id: str
    seasons: List[TeamSeasonSummary] = []
    roster: List[RosterEntry] = []

