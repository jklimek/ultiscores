"""Spirit of the Game schemas."""
from typing import Optional
from pydantic import Field
from src.schemas.base import CamelCaseModel


class SpiritRubric(CamelCaseModel):
    """Spirit rubric scores (0-4 each)."""
    rules_knowledge: int = Field(ge=0, le=4)
    fouls: int = Field(ge=0, le=4)
    fairness: int = Field(ge=0, le=4)
    positive_attitude: int = Field(ge=0, le=4)
    communication: int = Field(ge=0, le=4)


class SpiritScoreBase(CamelCaseModel):
    """Base spirit score schema."""
    rubric: SpiritRubric
    total: int = Field(ge=0, le=20)
    notes: Optional[str] = None


class SpiritScoreCreate(SpiritScoreBase):
    """Schema for creating a spirit score."""
    match_id: str
    team_id: str  # Team giving the score
    opponent_team_id: str  # Team receiving the score


class SpiritScore(SpiritScoreBase):
    """Full spirit score schema."""
    team_id: str
    opponent_team_id: str
    match_id: str
    

