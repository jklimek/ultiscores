"""Team Statistics model."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class TeamStats(Base):
    """Team statistics for matches and tournaments."""
    
    __tablename__ = "team_stats"
    __table_args__ = (
        UniqueConstraint('team_id', 'tournament_id', 'match_id', name='unique_team_stats'),
    )
    
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=True, index=True)  # Null for tournament totals
    
    # Game statistics
    holds = Column(Integer, default=0)  # Points won on offense
    breaks = Column(Integer, default=0)  # Points won on defense
    offensive_efficiency = Column(Float, default=0.0)  # holds / (holds + opponent breaks)
    possession_percentage = Column(Float, default=0.0)  # Time with disc
    turnovers = Column(Integer, default=0)
    completions = Column(Integer, default=0)
    pulls = Column(Integer, default=0)
    
    # Relationships
    team = relationship("Team", back_populates="team_stats")
    tournament = relationship("Tournament", back_populates="team_stats")
    match = relationship("Match", back_populates="team_stats")
    
    def __repr__(self):
        return f"<TeamStats(team={self.team_id}, holds={self.holds}, breaks={self.breaks})>"

