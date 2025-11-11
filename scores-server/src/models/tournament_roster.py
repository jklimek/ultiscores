"""Tournament Roster model."""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class TournamentRoster(Base):
    """Tournament roster linking players to teams for specific tournaments."""
    
    __tablename__ = "tournament_rosters"
    __table_args__ = (
        UniqueConstraint('tournament_id', 'team_id', 'player_id', name='unique_roster_entry'),
    )
    
    id = Column(String, primary_key=True, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    jersey_number = Column(Integer, nullable=True)
    is_captain = Column(Boolean, default=False)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="tournament_rosters")
    team = relationship("Team", back_populates="tournament_rosters")
    player = relationship("Player", back_populates="tournament_rosters")
    
    def __repr__(self):
        return f"<TournamentRoster(tournament={self.tournament_id}, team={self.team_id}, player={self.player_id})>"

