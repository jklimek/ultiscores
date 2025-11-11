"""Team endpoints."""
from typing import List, Optional
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models import (
    Team as TeamModel,
    TournamentRoster as TournamentRosterModel,
    Tournament as TournamentModel,
    Player as PlayerModel,
    Match as MatchModel
)
from src.schemas import Team, TeamCreate, TeamUpdate
from src.schemas.common import Division
from src.schemas.team import TeamSeasonSummary, RosterEntry
from src.schemas.player import Player as PlayerSchema

router = APIRouter()


async def build_team_response(team: TeamModel, db: AsyncSession) -> dict:
    """Build complete team response with seasons and roster."""
    # Get tournament roster entries for this team
    roster_query = select(TournamentRosterModel).options(
        selectinload(TournamentRosterModel.player),
        selectinload(TournamentRosterModel.tournament)
    ).where(TournamentRosterModel.team_id == team.id)
    
    roster_result = await db.execute(roster_query)
    roster_entries = roster_result.scalars().all()
    
    # Build roster array with full player data
    roster = []
    tournament_participation = defaultdict(lambda: {"tournaments": [], "division": None})
    
    for entry in roster_entries:
        if entry.player:
            # Add to roster - match frontend playerSchema exactly
            roster.append({
                "tournamentId": entry.tournament_id,
                "player": {
                    "id": entry.player.id,
                    "jerseyNumber": entry.jersey_number,  # From tournament roster
                    "name": {
                        "first": entry.player.first_name,
                        "last": entry.player.last_name,
                        "display": f"{entry.player.first_name} {entry.player.last_name}"
                    },
                    "pronouns": entry.player.pronouns,
                    "nationality": entry.player.nationality,
                    "dateOfBirth": str(entry.player.date_of_birth) if entry.player.date_of_birth else None,
                    "heightCm": entry.player.height_cm,
                    "roles": entry.player.roles or [],
                    "throws": entry.player.throws,
                    "dominantPositions": entry.player.dominant_positions or [],
                    "profileImageUrl": entry.player.profile_image_url,
                    "clubHistory": [],  # TODO: Calculate from tournament_rosters
                    "stats": None  # TODO: Aggregate from player_stats
                },
                "jerseyNumber": entry.jersey_number,
                "captain": entry.is_captain
            })
            
            # Track tournament participation for seasons
            if entry.tournament:
                season_id = entry.tournament.season_id
                if tournament_participation[season_id]["division"] is None:
                    tournament_participation[season_id]["division"] = entry.tournament.division
                
                tournament_participation[season_id]["tournaments"].append({
                    "tournamentId": entry.tournament.id,
                    "tournamentName": entry.tournament.name,
                    "placement": None,  # TODO: Calculate from standings
                    "wins": 0,  # TODO: Calculate from matches
                    "losses": 0  # TODO: Calculate from matches
                })
    
    # Build seasons array
    seasons = []
    for season_id, data in tournament_participation.items():
        seasons.append({
            "season": season_id,
            "division": data["division"],
            "tournaments": data["tournaments"]
        })
    
    # Build team dict
    team_dict = {
        "id": team.id,
        "name": team.name,
        "shortName": team.short_name,
        "slug": team.slug,
        "division": team.division,
        "clubName": team.club_name,
        "city": team.city,
        "country": team.country,
        "foundedYear": team.founded_year,
        "primaryColor": team.primary_color,
        "secondaryColor": team.secondary_color,
        "crestUrl": team.crest_url,
        "website": team.website,
        "seasons": seasons,
        "roster": roster
    }
    
    return team_dict


@router.get("/", response_model=List[Team])
async def list_teams(
    season_id: Optional[str] = Query(None),
    division: Optional[Division] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List teams with optional filters."""
    query = select(TeamModel)
    
    if division:
        query = query.where(TeamModel.division == division.value)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                TeamModel.name.ilike(search_pattern),
                TeamModel.city.ilike(search_pattern),
                TeamModel.club_name.ilike(search_pattern)
            )
        )
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Build complete responses for each team
    team_responses = []
    for team in teams:
        team_data = await build_team_response(team, db)
        team_responses.append(team_data)
    
    return team_responses


@router.get("/{team_id}", response_model=Team)
async def get_team(
    team_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific team with complete roster and season history."""
    result = await db.execute(
        select(TeamModel).where(
            or_(
                TeamModel.id == team_id,
                TeamModel.slug == team_id
            )
        )
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Build complete response with seasons and roster
    team_data = await build_team_response(team, db)
    return team_data


@router.post("/", response_model=Team, status_code=201)
async def create_team(
    team: TeamCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new team."""
    db_team = TeamModel(**team.model_dump())
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team


@router.patch("/{team_id}", response_model=Team)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a team."""
    result = await db.execute(
        select(TeamModel).where(TeamModel.id == team_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    for key, value in team_update.model_dump(exclude_unset=True).items():
        setattr(team, key, value)
    
    await db.commit()
    await db.refresh(team)
    return team

