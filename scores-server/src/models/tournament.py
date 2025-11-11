"""Tournament model."""
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship

from src.database import Base


class Tournament(Base):
    """Tournament model representing an Ultimate Frisbee tournament."""
    
    __tablename__ = "tournaments"
    
    id = Column(String, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    season_id = Column(String, ForeignKey("seasons.id"), nullable=False)
    division = Column(String, nullable=False)  # open, women, mixed, junior, masters
    start_date = Column(String, nullable=False)  # ISO format date
    end_date = Column(String, nullable=False)  # ISO format date
    status = Column(String, nullable=False, default="upcoming")  # upcoming, in_progress, completed, cancelled
    venue_id = Column(String, ForeignKey("venues.id"), nullable=False)
    
    # Tournament settings stored as JSON
    settings = Column(JSON, nullable=True)
    # {
    #   "format": "power_pools",  # pool, swiss, power_pools, single_elim, double_elim
    #   "pool_count": 2,
    #   "teams_per_pool": 4,
    #   "advancement": {...},
    #   "rest_periods": 1,
    #   "match_duration_minutes": 75,
    #   "field_count": 2,
    #   "cap_at": 15,
    #   "soft_cap_minutes": 90,
    #   "hard_cap_minutes": 110
    # }
    
    # Organiser info stored as JSON
    organiser = Column(JSON, nullable=True)
    # {"name": "PSGU", "website": "https://frisbee.pl", "contactEmail": "..."}
    
    # Teams participating (stored as JSON with seeds)
    teams = Column(JSON, nullable=False)  # [{"teamId": "...", "seed": 1}, ...]
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    season = relationship("Season", back_populates="tournaments")
    venue = relationship("Venue", back_populates="tournaments")
    stages = relationship("Stage", back_populates="tournament", cascade="all, delete-orphan", order_by="Stage.order")
    matches = relationship("Match", back_populates="tournament", cascade="all, delete-orphan")
    tournament_rosters = relationship("TournamentRoster", back_populates="tournament", cascade="all, delete-orphan")
    player_stats = relationship("PlayerStats", back_populates="tournament", cascade="all, delete-orphan")
    team_stats = relationship("TeamStats", back_populates="tournament", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tournament(id={self.id}, name={self.name}, status={self.status})>"

