"""Season endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models import Season as SeasonModel
from src.schemas import Season, SeasonSummary

router = APIRouter()


def build_season_response(season: SeasonModel) -> dict:
    """Build season response matching frontend schema."""
    return {
        "id": season.id,
        "label": season.label,
        "year": season.year,
        "divisions": [],  # TODO: Calculate from tournaments in this season
        "tournaments": []  # TODO: Load tournaments for this season
    }


@router.get("/", response_model=List[SeasonSummary])
async def list_seasons(
    db: AsyncSession = Depends(get_db)
):
    """Get all seasons."""
    result = await db.execute(
        select(SeasonModel).order_by(SeasonModel.year.desc())
    )
    seasons = result.scalars().all()
    return [build_season_response(season) for season in seasons]


@router.get("/{season_id}", response_model=SeasonSummary)
async def get_season(
    season_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific season."""
    result = await db.execute(
        select(SeasonModel).where(SeasonModel.id == season_id)
    )
    season = result.scalar_one_or_none()
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    return build_season_response(season)

