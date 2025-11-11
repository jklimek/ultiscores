"""Player model."""
from sqlalchemy import Column, String, Integer, Float, JSON, Date
from sqlalchemy.orm import relationship

from src.database import Base


class Player(Base):
    """Player model representing an Ultimate Frisbee player."""
    
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    pronouns = Column(String, nullable=True)
    nationality = Column(String, nullable=True, default="POL")
    date_of_birth = Column(Date, nullable=True)
    height_cm = Column(Float, nullable=True)
    throws = Column(String, nullable=True)  # left, right, both
    roles = Column(JSON, nullable=True)  # ["handler", "cutter", "flex"]
    dominant_positions = Column(JSON, nullable=True)  # ["offense", "defense"]
    profile_image_url = Column(String, nullable=True)
    
    # Relationships
    tournament_rosters = relationship("TournamentRoster", back_populates="player", cascade="all, delete-orphan")
    player_stats = relationship("PlayerStats", back_populates="player", cascade="all, delete-orphan")
    match_events = relationship("MatchEvent", back_populates="player")
    
    def __repr__(self):
        return f"<Player(id={self.id}, name={self.first_name} {self.last_name})>"

