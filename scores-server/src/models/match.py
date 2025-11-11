"""Match model."""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from src.database import Base


class Match(Base):
    """Match model representing a game between two teams."""
    
    __tablename__ = "matches"
    
    id = Column(String, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False)
    stage_id = Column(String, ForeignKey("stages.id"), nullable=True)
    pool_id = Column(String, ForeignKey("pools.id"), nullable=True)
    division = Column(String, nullable=False)
    round = Column(String, nullable=False)  # "Pool Play", "Quarterfinals", etc.
    
    # Teams
    home_team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    
    # Scheduling
    start_time = Column(String, nullable=False)  # ISO format datetime
    end_time = Column(String, nullable=True)
    estimated_duration_minutes = Column(Integer, default=75)
    field_id = Column(String, nullable=True)
    field_label = Column(String, nullable=True)
    
    # Match state
    status = Column(String, nullable=False, default="scheduled")  # scheduled, live, halftime, final, cancelled, delayed
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    home_timeouts = Column(Integer, default=2)
    away_timeouts = Column(Integer, default=2)
    
    # Game rules
    cap_at = Column(Integer, nullable=True)  # Point cap (e.g., 15)
    soft_cap_minutes = Column(Integer, nullable=True)  # Soft cap time
    hard_cap_minutes = Column(Integer, nullable=True)  # Hard cap time
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    stage = relationship("Stage", back_populates="matches")
    pool = relationship("Pool", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan", order_by="MatchEvent.sequence")
    player_stats = relationship("PlayerStats", back_populates="match", cascade="all, delete-orphan")
    team_stats = relationship("TeamStats", back_populates="match", cascade="all, delete-orphan")
    spirit_scores = relationship("SpiritScore", back_populates="match", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Match(id={self.id}, home={self.home_team_id} vs away={self.away_team_id}, {self.home_score}-{self.away_score})>"

