"""Player endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.database import get_db
from src.models import Player as PlayerModel
from src.schemas import Player, PlayerCreate, PlayerUpdate

router = APIRouter()


def build_player_response(player: PlayerModel) -> dict:
    """Build player response matching frontend schema."""
    return {
        "id": player.id,
        "firstName": player.first_name,  # Backend schema expects these
        "lastName": player.last_name,
        "jerseyNumber": None,  # Only available in tournament roster context
        "name": {
            "first": player.first_name,
            "last": player.last_name,
            "display": f"{player.first_name} {player.last_name}"
        },
        "pronouns": player.pronouns,
        "nationality": player.nationality,
        "dateOfBirth": str(player.date_of_birth) if player.date_of_birth else None,
        "heightCm": player.height_cm,
        "roles": player.roles or [],
        "throws": player.throws,
        "dominantPositions": player.dominant_positions or [],
        "profileImageUrl": player.profile_image_url,
        "clubHistory": [],  # TODO: Calculate from tournament_rosters
        "stats": None  # TODO: Aggregate from player_stats
    }


@router.get("/", response_model=List[Player])
async def list_players(
    team_id: Optional[str] = Query(None),
    tournament_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List players with optional filters."""
    query = select(PlayerModel)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                PlayerModel.first_name.ilike(search_pattern),
                PlayerModel.last_name.ilike(search_pattern)
            )
        )
    
    # TODO: Add filtering by team_id and tournament_id through joins
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    players = result.scalars().all()
    
    return [build_player_response(player) for player in players]


@router.get("/{player_id}", response_model=Player)
async def get_player(
    player_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific player."""
    result = await db.execute(
        select(PlayerModel).where(PlayerModel.id == player_id)
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return build_player_response(player)


@router.post("/", response_model=Player, status_code=201)
async def create_player(
    player: PlayerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new player."""
    db_player = PlayerModel(**player.model_dump())
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)
    return db_player


@router.patch("/{player_id}", response_model=Player)
async def update_player(
    player_id: str,
    player_update: PlayerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a player."""
    result = await db.execute(
        select(PlayerModel).where(PlayerModel.id == player_id)
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    for key, value in player_update.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    
    await db.commit()
    await db.refresh(player)
    return player

