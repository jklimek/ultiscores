"""Venue model."""
from sqlalchemy import Column, String, Float, JSON
from sqlalchemy.orm import relationship

from src.database import Base


class Venue(Base):
    """Venue model representing a tournament location."""
    
    __tablename__ = "venues"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default="Europe/Warsaw")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    fields = Column(JSON, nullable=False)  # [{"id": "1", "label": "Field 1", "surface": "grass"}]
    
    # Relationships
    tournaments = relationship("Tournament", back_populates="venue")
    
    def __repr__(self):
        return f"<Venue(id={self.id}, name={self.name}, city={self.city})>"

