"""Tournament endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models import (
    Tournament as TournamentModel,
    SpiritScore as SpiritScoreModel,
    Match as MatchModel,
)
from src.schemas import Tournament, TournamentCreate, TournamentUpdate, TournamentSummary, SpiritScore
from src.schemas.common import Division, TournamentStatus

router = APIRouter()


@router.get("/", response_model=List[Tournament])
async def list_tournaments(
    season_id: Optional[str] = Query(None),
    division: Optional[Division] = Query(None),
    status: Optional[TournamentStatus] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List tournaments with optional filters."""
    from src.models import Stage as StageModel
    
    query = select(TournamentModel).options(
        selectinload(TournamentModel.venue),
        selectinload(TournamentModel.stages).selectinload(StageModel.pools)
    )
    
    if season_id:
        query = query.where(TournamentModel.season_id == season_id)
    
    if division:
        query = query.where(TournamentModel.division == division.value)
    
    if status:
        query = query.where(TournamentModel.status == status.value)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(TournamentModel.name.ilike(search_pattern))
    
    query = query.order_by(TournamentModel.start_date.desc())
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    tournaments = result.scalars().all()
    return tournaments


@router.get("/{tournament_id}", response_model=Tournament)
async def get_tournament(
    tournament_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tournament with stages, pools, and standings."""
    from src.models import Stage as StageModel
    
    result = await db.execute(
        select(TournamentModel)
        .options(
            selectinload(TournamentModel.venue),
            selectinload(TournamentModel.stages).selectinload(StageModel.pools)
        )
        .where(
            or_(
                TournamentModel.id == tournament_id,
                TournamentModel.slug == tournament_id
            )
        )
    )
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.get("/{tournament_id}/spirit", response_model=List[SpiritScore])
async def get_tournament_spirit_scores(
    tournament_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get spirit scores for all matches in a tournament."""
    result = await db.execute(
        select(SpiritScoreModel)
        .join(MatchModel, MatchModel.id == SpiritScoreModel.match_id)
        .where(MatchModel.tournament_id == tournament_id)
    )
    spirit_scores = result.scalars().all()
    return spirit_scores


@router.post("/", response_model=Tournament, status_code=201)
async def create_tournament(
    tournament: TournamentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tournament."""
    db_tournament = TournamentModel(**tournament.model_dump())
    db.add(db_tournament)
    await db.commit()
    await db.refresh(db_tournament)
    return db_tournament


@router.patch("/{tournament_id}", response_model=Tournament)
async def update_tournament(
    tournament_id: str,
    tournament_update: TournamentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a tournament."""
    result = await db.execute(
        select(TournamentModel).where(TournamentModel.id == tournament_id)
    )
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    for key, value in tournament_update.model_dump(exclude_unset=True).items():
        setattr(tournament, key, value)
    
    await db.commit()
    await db.refresh(tournament)
    return tournament

