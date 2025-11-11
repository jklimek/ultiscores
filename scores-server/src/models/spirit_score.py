"""Spirit of the Game Score model."""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from src.database import Base


class SpiritScore(Base):
    """Spirit of the Game scores submitted after matches."""
    
    __tablename__ = "spirit_scores"
    __table_args__ = (
        UniqueConstraint('match_id', 'team_id', name='unique_spirit_score'),
    )
    
    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)  # Team giving the score
    opponent_team_id = Column(String, ForeignKey("teams.id"), nullable=False)  # Team receiving the score
    
    # Spirit rubric (each category 0-4 points)
    rules_knowledge = Column(Integer, nullable=False)
    fouls = Column(Integer, nullable=False)
    fairness = Column(Integer, nullable=False)
    positive_attitude = Column(Integer, nullable=False)
    communication = Column(Integer, nullable=False)
    
    # Total (0-20 points)
    total = Column(Integer, nullable=False)
    
    # Optional notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="spirit_scores")
    team = relationship("Team", foreign_keys=[team_id], back_populates="spirit_scores_given")
    opponent_team = relationship("Team", foreign_keys=[opponent_team_id], back_populates="spirit_scores_received")
    
    def __repr__(self):
        return f"<SpiritScore(match={self.match_id}, team={self.team_id}, total={self.total})>"

