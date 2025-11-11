"""Pool model."""
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from src.database import Base


class Pool(Base):
    """Pool model representing a group within a stage."""
    
    __tablename__ = "pools"
    
    id = Column(String, primary_key=True, index=True)
    stage_id = Column(String, ForeignKey("stages.id"), nullable=False)
    label = Column(String, nullable=False)  # "Pool A", "Championship Pool", etc.
    
    # Teams in this pool with their seeds
    teams = Column(JSON, nullable=False)  # [{"teamId": "...", "seed": 1}, ...]
    
    # Relationships
    stage = relationship("Stage", back_populates="pools")
    matches = relationship("Match", back_populates="pool")
    
    def __repr__(self):
        return f"<Pool(id={self.id}, label={self.label})>"

