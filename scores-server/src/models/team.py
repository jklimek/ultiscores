"""Team model."""
from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.orm import relationship

from src.database import Base


class Team(Base):
    """Team model representing an Ultimate Frisbee team."""
    
    __tablename__ = "teams"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    short_name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    division = Column(String, nullable=False)  # open, women, mixed, junior, masters
    club_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True, default="Poland")
    founded_year = Column(Integer, nullable=True)
    primary_color = Column(String, nullable=True)
    secondary_color = Column(String, nullable=True)
    crest_url = Column(String, nullable=True)
    website = Column(String, nullable=True)
    
    # Relationships
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    tournament_rosters = relationship("TournamentRoster", back_populates="team", cascade="all, delete-orphan")
    team_stats = relationship("TeamStats", back_populates="team", cascade="all, delete-orphan")
    spirit_scores_given = relationship(
        "SpiritScore",
        foreign_keys="SpiritScore.team_id",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    spirit_scores_received = relationship(
        "SpiritScore",
        foreign_keys="SpiritScore.opponent_team_id",
        back_populates="opponent_team",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, division={self.division})>"

