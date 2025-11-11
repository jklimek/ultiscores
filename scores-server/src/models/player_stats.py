"""Player Statistics model."""
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class PlayerStats(Base):
    """Player statistics for matches and tournaments."""
    
    __tablename__ = "player_stats"
    __table_args__ = (
        UniqueConstraint('player_id', 'tournament_id', 'match_id', name='unique_player_stats'),
    )
    
    id = Column(String, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=True, index=True)  # Null for tournament totals
    
    # Statistics
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    blocks = Column(Integer, default=0)  # Defensive blocks (D's)
    turnovers = Column(Integer, default=0)
    points_played = Column(Integer, default=0)
    
    # Relationships
    player = relationship("Player", back_populates="player_stats")
    tournament = relationship("Tournament", back_populates="player_stats")
    match = relationship("Match", back_populates="player_stats")
    
    def __repr__(self):
        return f"<PlayerStats(player={self.player_id}, goals={self.goals}, assists={self.assists})>"

