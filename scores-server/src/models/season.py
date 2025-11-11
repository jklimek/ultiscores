"""Season model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Season(Base):
    """Season model representing a tournament season."""
    
    __tablename__ = "seasons"
    
    id = Column(String, primary_key=True, index=True)
    label = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Relationships
    tournaments = relationship("Tournament", back_populates="season", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Season(id={self.id}, label={self.label}, year={self.year})>"

