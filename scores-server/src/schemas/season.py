"""Season schemas."""
from typing import List
from src.schemas.base import CamelCaseModel
from src.schemas.common import Division


class SeasonBase(CamelCaseModel):
    """Base season schema."""
    label: str
    year: int


class SeasonCreate(SeasonBase):
    """Schema for creating a season."""
    id: str


class Season(SeasonBase):
    """Full season schema."""
    id: str


class TournamentSummaryInSeason(CamelCaseModel):
    """Tournament summary for season listing."""
    id: str
    slug: str
    name: str
    start_date: str = ""
    end_date: str = ""
    status: str
    division: Division


class SeasonSummary(Season):
    """Season with tournament list."""
    divisions: List[Division] = []
    tournaments: List[TournamentSummaryInSeason] = []

