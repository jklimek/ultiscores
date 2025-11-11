"""Match Event model."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship

from src.database import Base


class MatchEvent(Base):
    """Match event model representing a discrete event during a match."""
    
    __tablename__ = "match_events"
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)  # Event order
    type = Column(String, nullable=False)  # goal, turnover, timeout, call, pull, period
    point_number = Column(Integer, nullable=False)
    elapsed_seconds = Column(Float, nullable=False)
    clock_label = Column(String, nullable=True)  # "12:34" format
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=True)
    summary = Column(String, nullable=True)  # Human-readable summary
    
    # Type-specific data stored as JSON
    data = Column(JSON, nullable=True)
    # For goal: {"scorerId": "...", "assisterId": "...", "offensiveLine": [...]}
    # For turnover: {"turnoverType": "block", "causedById": "...", "reason": "..."}
    # For timeout: {"timeoutType": "team"}
    # For call: {"callType": "foul", "resolved": true}
    # For pull: {"pullingTeamId": "..."}
    # For period: {"label": "Halftime"}
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    match = relationship("Match", back_populates="events")
    team = relationship("Team")
    player = relationship("Player", back_populates="match_events")
    
    def __repr__(self):
        return f"<MatchEvent(id={self.id}, type={self.type}, seq={self.sequence})>"

