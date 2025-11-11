"""Stage model."""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base


class Stage(Base):
    """Stage model representing a tournament stage (pools, bracket, placement, etc.)."""
    
    __tablename__ = "stages"
    
    id = Column(String, primary_key=True, index=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False)
    name = Column(String, nullable=False)
    stage_type = Column(String, nullable=False)  # pool, round_robin, bracket, placement, relegation, swiss
    division = Column(String, nullable=False)
    order = Column(Integer, nullable=False, default=0)  # Stage order in tournament
    
    # Relationships
    tournament = relationship("Tournament", back_populates="stages")
    pools = relationship("Pool", back_populates="stage", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="stage")
    
    def __repr__(self):
        return f"<Stage(id={self.id}, name={self.name}, type={self.stage_type})>"

