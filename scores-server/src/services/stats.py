"""Statistics calculation engine for Ultimate Frisbee matches.

Calculates:
- Holds: points won on offense (team started with possession)
- Breaks: points won on defense (opponent started with possession)
- Possession time: percentage of disc possession per team
- Player stats: goals, assists, blocks, turnovers, points played
"""
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class MatchStatistics:
    """Calculate match statistics from event timeline."""
    
    def __init__(self, events: List[dict], home_team_id: str, away_team_id: str):
        """
        Initialize with match events.
        
        Args:
            events: List of match events in order
            home_team_id: Home team ID
            away_team_id: Away team ID
        """
        self.events = events
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        
    def calculate_all(self) -> Dict:
        """Calculate all statistics."""
        return {
            "holds_breaks": self.calculate_holds_breaks(),
            "possession": self.calculate_possession(),
            "turnovers": self.calculate_turnovers(),
            "player_stats": self.calculate_player_stats(),
            "team_stats": self.calculate_team_stats(),
        }
    
    def calculate_holds_breaks(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate holds and breaks for each team.
        
        Holds: points won on offense (team that pulled on defense or received pull)
        Breaks: points won on defense (team that pulled on offense)
        
        Returns:
            {
                "home": {"holds": 5, "breaks": 2},
                "away": {"holds": 4, "breaks": 3}
            }
        """
        holds = {self.home_team_id: 0, self.away_team_id: 0}
        breaks = {self.home_team_id: 0, self.away_team_id: 0}
        
        # Track possession at start of each point
        point_possession = {}  # point_number -> team_id with initial possession
        current_point = 0
        halftime_point = None
        
        for event in self.events:
            event_type = event.get("type")
            point = event.get("point", 0)
            
            if point != current_point:
                current_point = point
            
            # Track halftime to handle possession flip
            if event_type == "period" and event.get("data", {}).get("label") == "Halftime":
                halftime_point = point
            
            # Pull determines initial possession
            if event_type == "pull":
                pulling_team = event.get("data", {}).get("pullingTeamId") or event.get("team_id")
                # Team that pulls is on defense, so opponent has possession
                if pulling_team == self.home_team_id:
                    point_possession[point] = self.away_team_id
                else:
                    point_possession[point] = self.home_team_id
            
            # Goal ends the point
            if event_type == "goal":
                scoring_team = event.get("team_id")
                if not scoring_team:
                    scoring_team = event.get("data", {}).get("scorerId")  # Fallback
                
                # Determine if this was a hold or break
                initial_possession = point_possession.get(point)
                if initial_possession:
                    if scoring_team == initial_possession:
                        # Hold: team with initial possession scored
                        holds[scoring_team] += 1
                    else:
                        # Break: team without initial possession scored
                        breaks[scoring_team] += 1
        
        return {
            "home": {
                "holds": holds[self.home_team_id],
                "breaks": breaks[self.home_team_id],
            },
            "away": {
                "holds": holds[self.away_team_id],
                "breaks": breaks[self.away_team_id],
            },
        }
    
    def calculate_possession(self) -> Dict[str, float]:
        """
        Calculate possession percentage for each team.
        
        Estimates possession based on event timestamps and turnover/goal events.
        
        Returns:
            {"home": 55.0, "away": 45.0}
        """
        possession_time = {self.home_team_id: 0.0, self.away_team_id: 0.0}
        current_possession = None
        last_time = 0.0
        
        for event in self.events:
            elapsed = event.get("elapsed_seconds", 0.0)
            event_type = event.get("type")
            
            # Add time to current possessing team
            if current_possession and elapsed > last_time:
                possession_time[current_possession] += (elapsed - last_time)
            
            # Possession changes
            if event_type == "pull":
                pulling_team = event.get("data", {}).get("pullingTeamId") or event.get("team_id")
                # Receiving team gets possession
                current_possession = self.away_team_id if pulling_team == self.home_team_id else self.home_team_id
            
            elif event_type == "turnover":
                # Possession switches to other team
                if current_possession == self.home_team_id:
                    current_possession = self.away_team_id
                else:
                    current_possession = self.home_team_id
            
            elif event_type == "goal":
                # Scoring team had possession up to goal
                scoring_team = event.get("team_id")
                if scoring_team:
                    current_possession = scoring_team
                # After goal, possession resets (other team pulls)
            
            last_time = elapsed
        
        # Calculate percentages
        total_time = sum(possession_time.values())
        if total_time > 0:
            return {
                "home": round(100 * possession_time[self.home_team_id] / total_time, 1),
                "away": round(100 * possession_time[self.away_team_id] / total_time, 1),
            }
        
        return {"home": 50.0, "away": 50.0}
    
    def calculate_turnovers(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate turnovers by type for each team.
        
        Returns:
            {
                "home": {"throwaway": 3, "drop": 2, "block": 1, ...},
                "away": {"throwaway": 2, "drop": 1, ...}
            }
        """
        turnovers = {
            self.home_team_id: defaultdict(int),
            self.away_team_id: defaultdict(int),
        }
        
        for event in self.events:
            if event.get("type") == "turnover":
                team_id = event.get("team_id")
                turnover_type = event.get("data", {}).get("turnoverType", "unknown")
                
                if team_id in turnovers:
                    turnovers[team_id][turnover_type] += 1
        
        return {
            "home": dict(turnovers[self.home_team_id]),
            "away": dict(turnovers[self.away_team_id]),
        }
    
    def calculate_player_stats(self) -> Dict[str, Dict]:
        """
        Calculate individual player statistics.
        
        Returns:
            {
                "player_id": {
                    "goals": 3,
                    "assists": 2,
                    "blocks": 1,
                    "turnovers": 2,
                    "points_played": 15
                },
                ...
            }
        """
        stats = defaultdict(lambda: {
            "goals": 0,
            "assists": 0,
            "blocks": 0,
            "turnovers": 0,
            "points_played": 0,
        })
        
        # Track which players played in which points
        players_in_points = defaultdict(set)
        
        for event in self.events:
            event_type = event.get("type")
            point = event.get("point", 0)
            player_id = event.get("player_id")
            data = event.get("data", {})
            
            # Count goals
            if event_type == "goal" and player_id:
                stats[player_id]["goals"] += 1
                players_in_points[point].add(player_id)
                
                # Count assists
                assister_id = data.get("assisterId")
                if assister_id:
                    stats[assister_id]["assists"] += 1
                    players_in_points[point].add(assister_id)
                
                # Track offensive line
                for line_player_id in data.get("offensiveLine", []):
                    players_in_points[point].add(line_player_id)
            
            # Count blocks (defensive turnovers)
            elif event_type == "turnover":
                turnover_type = data.get("turnoverType")
                caused_by_id = data.get("causedById")
                
                if turnover_type in ["block", "callahan"] and caused_by_id:
                    stats[caused_by_id]["blocks"] += 1
                    players_in_points[point].add(caused_by_id)
                
                # Track turnover thrower
                if player_id and turnover_type not in ["callahan"]:
                    stats[player_id]["turnovers"] += 1
                    players_in_points[point].add(player_id)
            
            # Track other event participants
            elif player_id:
                players_in_points[point].add(player_id)
        
        # Calculate points played
        for point, players in players_in_points.items():
            for player_id in players:
                stats[player_id]["points_played"] += 1
        
        return dict(stats)
    
    def calculate_team_stats(self) -> Dict[str, Dict]:
        """
        Calculate aggregate team statistics.
        
        Returns:
            {
                "home": {
                    "holds": 5,
                    "breaks": 2,
                    "offensive_efficiency": 0.71,  # holds / (holds + opp breaks)
                    "turnovers": 12,
                    "completions": 145
                },
                ...
            }
        """
        holds_breaks = self.calculate_holds_breaks()
        turnovers = self.calculate_turnovers()
        
        home_holds = holds_breaks["home"]["holds"]
        home_breaks = holds_breaks["home"]["breaks"]
        away_holds = holds_breaks["away"]["holds"]
        away_breaks = holds_breaks["away"]["breaks"]
        
        # Offensive efficiency: holds / (holds + opponent breaks)
        home_eff = home_holds / (home_holds + away_breaks) if (home_holds + away_breaks) > 0 else 0.0
        away_eff = away_holds / (away_holds + home_breaks) if (away_holds + home_breaks) > 0 else 0.0
        
        return {
            "home": {
                "holds": home_holds,
                "breaks": home_breaks,
                "offensive_efficiency": round(home_eff, 3),
                "turnovers": sum(turnovers["home"].values()),
            },
            "away": {
                "holds": away_holds,
                "breaks": away_breaks,
                "offensive_efficiency": round(away_eff, 3),
                "turnovers": sum(turnovers["away"].values()),
            },
        }


async def calculate_match_statistics(match_id: str, db) -> Dict:
    """
    Calculate statistics for a match.
    
    Args:
        match_id: Match ID
        db: Database session
        
    Returns:
        Dictionary of statistics
    """
    from sqlalchemy import select
    from src.models import Match, MatchEvent
    
    # Get match and events
    result = await db.execute(
        select(Match).where(Match.id == match_id)
    )
    match = result.scalar_one_or_none()
    if not match:
        return {}
    
    result = await db.execute(
        select(MatchEvent)
        .where(MatchEvent.match_id == match_id)
        .order_by(MatchEvent.sequence)
    )
    events = result.scalars().all()
    
    # Convert events to dict format
    event_dicts = [
        {
            "type": event.type,
            "point": event.point_number,
            "elapsed_seconds": event.elapsed_seconds,
            "team_id": event.team_id,
            "player_id": event.player_id,
            "data": event.data or {},
        }
        for event in events
    ]
    
    # Calculate statistics
    calculator = MatchStatistics(
        event_dicts,
        match.home_team_id,
        match.away_team_id
    )
    
    return calculator.calculate_all()

