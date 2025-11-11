"""Admin endpoints for tournament management."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import MatchEvent as MatchEventModel, Match as MatchModel, SpiritScore as SpiritScoreModel
from src.schemas import MatchEventCreate, SpiritScoreCreate, SpiritScore, MatchEvent
from sqlalchemy import select

router = APIRouter()


@router.post("/matches/{match_id}/events", response_model=MatchEvent, status_code=201)
async def create_match_event(
    match_id: str,
    event: MatchEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a match event (goal, turnover, timeout, etc.)."""
    # Verify match exists
    result = await db.execute(
        select(MatchModel).where(MatchModel.id == match_id)
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get next sequence number
    result = await db.execute(
        select(MatchEventModel)
        .where(MatchEventModel.match_id == match_id)
        .order_by(MatchEventModel.sequence.desc())
    )
    last_event = result.scalar_one_or_none()
    next_sequence = (last_event.sequence + 1) if last_event else 0
    
    # Create event
    db_event = MatchEventModel(
        id=str(uuid.uuid4()),
        match_id=match_id,
        sequence=next_sequence,
        **event.model_dump(exclude={'match_id'})
    )
    db.add(db_event)
    
    # Update match scores if goal
    if event.type == "goal":
        if event.team_id == match.home_team_id:
            match.home_score += 1
        elif event.team_id == match.away_team_id:
            match.away_score += 1
    
    # Update timeouts if timeout
    if event.type == "timeout" and event.data and event.data.get("timeoutType") == "team":
        if event.team_id == match.home_team_id:
            match.home_timeouts = max(0, match.home_timeouts - 1)
        elif event.team_id == match.away_team_id:
            match.away_timeouts = max(0, match.away_timeouts - 1)
    
    await db.commit()
    await db.refresh(db_event)
    
    # TODO: Broadcast event via WebSocket
    
    return db_event


@router.post("/spirit", response_model=SpiritScore, status_code=201)
async def create_spirit_score(
    spirit: SpiritScoreCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit a spirit score for a match."""
    # Verify match exists
    result = await db.execute(
        select(MatchModel).where(MatchModel.id == spirit.match_id)
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    db_spirit = SpiritScoreModel(
        id=str(uuid.uuid4()),
        **spirit.model_dump()
    )
    db.add(db_spirit)
    await db.commit()
    await db.refresh(db_spirit)
    
    # TODO: Broadcast spirit update via WebSocket
    
    return db_spirit

