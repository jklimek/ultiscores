"""Match endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models import Match as MatchModel, MatchEvent as MatchEventModel
from src.schemas import Match, MatchCreate, MatchUpdate, MatchSummary, MatchEvent
from src.schemas.common import Division, MatchStatus

router = APIRouter()


def build_match_summary(match: MatchModel) -> dict:
    """Build match summary response from database model."""
    return {
        "slug": match.slug,
        "division": match.division,
        "round": match.round,
        "startTime": match.start_time,
        "endTime": match.end_time,
        "estimatedDurationMinutes": match.estimated_duration_minutes,
        "fieldId": match.field_id,
        "fieldLabel": match.field_label,
        "status": match.status,
        "capAt": match.cap_at,
        "softCapMinutes": match.soft_cap_minutes,
        "hardCapMinutes": match.hard_cap_minutes,
        "id": match.id,
        "tournamentId": match.tournament_id,
        "home": {
            "teamId": match.home_team_id,
            "score": match.home_score or 0,
            "timeoutsRemaining": match.home_timeouts or 2,
            "spiritScore": None  # TODO: Load from spirit_scores table
        },
        "away": {
            "teamId": match.away_team_id,
            "score": match.away_score or 0,
            "timeoutsRemaining": match.away_timeouts or 2,
            "spiritScore": None  # TODO: Load from spirit_scores table
        },
        "updatedAt": match.updated_at.isoformat() if match.updated_at else None
    }


@router.get("/", response_model=List[MatchSummary])
async def list_matches(
    tournament_id: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    division: Optional[Division] = Query(None),
    status: Optional[MatchStatus] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List matches with optional filters."""
    query = select(MatchModel)
    
    if tournament_id:
        query = query.where(MatchModel.tournament_id == tournament_id)
    
    if team_id:
        query = query.where(
            (MatchModel.home_team_id == team_id) | (MatchModel.away_team_id == team_id)
        )
    
    if division:
        query = query.where(MatchModel.division == division.value)
    
    if status:
        query = query.where(MatchModel.status == status.value)
    
    query = query.order_by(MatchModel.start_time)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Build response with proper structure
    return [build_match_summary(match) for match in matches]


@router.get("/{match_id}", response_model=Match)
async def get_match(
    match_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific match with full event timeline."""
    result = await db.execute(
        select(MatchModel).where(MatchModel.id == match_id)
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Build full match response
    match_dict = build_match_summary(match)
    match_dict.update({
        "stageId": match.stage_id,
        "poolId": match.pool_id,
        "venue": None,  # TODO: Load from tournament.venue
        "events": [],   # TODO: Load match events
        "stats": None,  # TODO: Calculate stats
        "broadcast": None,
        "officials": None
    })
    return match_dict


@router.get("/{match_id}/events", response_model=List[MatchEvent])
async def get_match_events(
    match_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get ordered list of match events."""
    result = await db.execute(
        select(MatchEventModel)
        .where(MatchEventModel.match_id == match_id)
        .order_by(MatchEventModel.sequence)
    )
    events = result.scalars().all()
    return events


@router.post("/", response_model=Match, status_code=201)
async def create_match(
    match: MatchCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new match."""
    db_match = MatchModel(**match.model_dump())
    db.add(db_match)
    await db.commit()
    await db.refresh(db_match)
    return db_match


@router.patch("/{match_id}", response_model=Match)
async def update_match(
    match_id: str,
    match_update: MatchUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a match."""
    result = await db.execute(
        select(MatchModel).where(MatchModel.id == match_id)
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    for key, value in match_update.model_dump(exclude_unset=True).items():
        setattr(match, key, value)
    
    await db.commit()
    await db.refresh(match)
    return match

