"""Venue schemas."""
from typing import Optional, List

from src.schemas.base import CamelCaseModel


class VenueField(CamelCaseModel):
    """Venue field information."""
    id: str
    label: str
    surface: Optional[str] = None  # grass, turf, indoor, sand


class VenueBase(CamelCaseModel):
    """Base venue schema."""
    name: str
    city: str
    country: str = "Poland"
    timezone: str = "Europe/Warsaw"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    fields: List[VenueField] = []


class VenueCreate(VenueBase):
    """Schema for creating a venue."""
    id: str


class Venue(VenueBase):
    """Full venue schema."""
    id: str

