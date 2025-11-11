"""Statistics schemas."""
from typing import Optional
from src.schemas.base import CamelCaseModel


class PlayerStats(CamelCaseModel):
    """Player statistics."""
    player_id: str
    tournament_id: str
    match_id: Optional[str] = None
    goals: int = 0
    assists: int = 0
    blocks: int = 0
    turnovers: int = 0
    points_played: int = 0
    


class TeamStats(CamelCaseModel):
    """Team statistics."""
    team_id: str
    tournament_id: str
    match_id: Optional[str] = None
    holds: int = 0
    breaks: int = 0
    offensive_efficiency: float = 0.0
    possession_percentage: float = 0.0
    turnovers: int = 0
    completions: int = 0
    pulls: int = 0
    

