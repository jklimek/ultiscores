"""Match scheduler with rest period enforcement and field allocation.

Ensures:
- Teams get configured rest periods between matches
- Fields are balanced
- Time slots are realistic
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from itertools import cycle


@dataclass
class ScheduledMatch:
    """Match with scheduling information."""
    match_id: str
    home_team_id: str
    away_team_id: str
    start_time: datetime
    field_id: str
    field_label: str
    estimated_duration_minutes: int


class MatchScheduler:
    """Schedule matches with rest periods and field allocation."""
    
    def __init__(
        self,
        start_time: datetime,
        field_count: int,
        match_duration_minutes: int = 75,
        turnaround_minutes: int = 15,
        rest_periods: int = 1,
    ):
        """
        Initialize scheduler.
        
        Args:
            start_time: Tournament start time
            field_count: Number of available fields
            match_duration_minutes: Average match duration
            turnaround_minutes: Time between matches on same field
            rest_periods: Minimum number of matches a team sits out between games
        """
        self.start_time = start_time
        self.field_count = field_count
        self.match_duration_minutes = match_duration_minutes
        self.turnaround_minutes = turnaround_minutes
        self.rest_periods = rest_periods
        
        # State tracking
        self.team_last_match: Dict[str, int] = {}  # team_id -> match_index
        self.field_availability: Dict[str, datetime] = {
            f"field-{i+1}": start_time for i in range(field_count)
        }
        self.scheduled_matches: List[ScheduledMatch] = []
    
    def schedule_matches(
        self, matches: List[Dict]
    ) -> List[ScheduledMatch]:
        """
        Schedule all matches respecting rest periods and field availability.
        
        Args:
            matches: List of match dictionaries with home_team_id, away_team_id, match_id
            
        Returns:
            List of scheduled matches with start_time and field_id
        """
        # Queue of matches to schedule
        match_queue = list(matches)
        match_index = 0
        attempts = 0
        max_attempts = len(matches) * 10  # Prevent infinite loops
        
        while match_queue and attempts < max_attempts:
            attempts += 1
            
            # Try to schedule the next match
            match = match_queue[0]
            home_team = match["home_team_id"]
            away_team = match["away_team_id"]
            
            # Check if both teams have rested enough
            home_last = self.team_last_match.get(home_team, -999)
            away_last = self.team_last_match.get(away_team, -999)
            
            matches_since_home = match_index - home_last
            matches_since_away = match_index - away_last
            
            if (matches_since_home > self.rest_periods and 
                matches_since_away > self.rest_periods):
                # Both teams have rested enough, schedule the match
                field_id, field_label, start_time = self._get_next_available_field()
                
                scheduled = ScheduledMatch(
                    match_id=match["match_id"],
                    home_team_id=home_team,
                    away_team_id=away_team,
                    start_time=start_time,
                    field_id=field_id,
                    field_label=field_label,
                    estimated_duration_minutes=self.match_duration_minutes,
                )
                
                self.scheduled_matches.append(scheduled)
                self.team_last_match[home_team] = match_index
                self.team_last_match[away_team] = match_index
                
                # Update field availability
                end_time = start_time + timedelta(
                    minutes=self.match_duration_minutes + self.turnaround_minutes
                )
                self.field_availability[field_id] = end_time
                
                # Remove from queue
                match_queue.pop(0)
                match_index += 1
            else:
                # Teams not rested enough, move to end of queue
                match_queue.append(match_queue.pop(0))
        
        # If we couldn't schedule all matches, schedule remaining without rest enforcement
        if match_queue:
            for match in match_queue:
                field_id, field_label, start_time = self._get_next_available_field()
                
                scheduled = ScheduledMatch(
                    match_id=match["match_id"],
                    home_team_id=match["home_team_id"],
                    away_team_id=match["away_team_id"],
                    start_time=start_time,
                    field_id=field_id,
                    field_label=field_label,
                    estimated_duration_minutes=self.match_duration_minutes,
                )
                
                self.scheduled_matches.append(scheduled)
                
                # Update field availability
                end_time = start_time + timedelta(
                    minutes=self.match_duration_minutes + self.turnaround_minutes
                )
                self.field_availability[field_id] = end_time
        
        return self.scheduled_matches
    
    def _get_next_available_field(self) -> tuple[str, str, datetime]:
        """
        Get the next available field and time slot.
        
        Returns:
            (field_id, field_label, start_time)
        """
        # Find field with earliest availability
        earliest_field = min(
            self.field_availability.items(),
            key=lambda x: x[1]
        )
        
        field_id = earliest_field[0]
        start_time = earliest_field[1]
        field_label = field_id.replace("field-", "Field ")
        
        return field_id, field_label, start_time
    
    def get_schedule_summary(self) -> Dict:
        """Get summary of scheduled matches."""
        if not self.scheduled_matches:
            return {}
        
        end_time = max(
            m.start_time + timedelta(minutes=m.estimated_duration_minutes)
            for m in self.scheduled_matches
        )
        
        duration = end_time - self.start_time
        
        return {
            "total_matches": len(self.scheduled_matches),
            "fields_used": self.field_count,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_hours": duration.total_seconds() / 3600,
            "matches_per_field": [
                len([m for m in self.scheduled_matches if m.field_id == f"field-{i+1}"])
                for i in range(self.field_count)
            ],
        }


async def schedule_tournament_matches(
    tournament_id: str,
    start_time: datetime,
    settings: Dict,
    db
) -> List[ScheduledMatch]:
    """
    Schedule all matches for a tournament.
    
    Args:
        tournament_id: Tournament ID
        start_time: Tournament start time
        settings: Tournament settings (field_count, rest_periods, etc.)
        db: Database session
        
    Returns:
        List of scheduled matches
    """
    from sqlalchemy import select
    from src.models import Match
    
    # Get all unscheduled matches
    result = await db.execute(
        select(Match)
        .where(Match.tournament_id == tournament_id)
        .where(Match.start_time == "")
        .order_by(Match.round)
    )
    matches = result.scalars().all()
    
    if not matches:
        return []
    
    # Create scheduler
    scheduler = MatchScheduler(
        start_time=start_time,
        field_count=settings.get("field_count", 2),
        match_duration_minutes=settings.get("match_duration_minutes", 75),
        turnaround_minutes=settings.get("turnaround_minutes", 15),
        rest_periods=settings.get("rest_periods", 1),
    )
    
    # Prepare matches for scheduling
    match_dicts = [
        {
            "match_id": m.id,
            "home_team_id": m.home_team_id,
            "away_team_id": m.away_team_id,
        }
        for m in matches
    ]
    
    # Schedule matches
    scheduled = scheduler.schedule_matches(match_dicts)
    
    # Update database
    for scheduled_match in scheduled:
        result = await db.execute(
            select(Match).where(Match.id == scheduled_match.match_id)
        )
        match = result.scalar_one()
        
        match.start_time = scheduled_match.start_time.isoformat()
        match.field_id = scheduled_match.field_id
        match.field_label = scheduled_match.field_label
    
    await db.commit()
    
    return scheduled


def optimize_pool_schedule(
    pool_matches: List[Dict],
    teams: List[str],
    field_count: int,
    rest_periods: int = 1
) -> List[List[Dict]]:
    """
    Optimize match order within a pool for better scheduling.
    
    Returns matches grouped by rounds where all teams can play simultaneously.
    
    Args:
        pool_matches: List of matches
        teams: List of team IDs in pool
        field_count: Available fields
        rest_periods: Rest periods required
        
    Returns:
        List of rounds, each containing matches that can be played simultaneously
    """
    rounds = []
    remaining = list(pool_matches)
    
    while remaining:
        # Try to build a round with as many matches as possible
        round_matches = []
        teams_in_round = set()
        
        for match in remaining[:]:
            home = match["home_team_id"]
            away = match["away_team_id"]
            
            # Can add this match if neither team is already playing
            if home not in teams_in_round and away not in teams_in_round:
                if len(round_matches) < field_count:
                    round_matches.append(match)
                    teams_in_round.add(home)
                    teams_in_round.add(away)
                    remaining.remove(match)
        
        if round_matches:
            rounds.append(round_matches)
        else:
            # Couldn't schedule any more matches optimally, add remaining
            rounds.append(remaining)
            break
    
    return rounds

