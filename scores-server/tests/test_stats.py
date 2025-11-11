"""Tests for statistics calculation."""
import pytest
from src.services.stats import MatchStatistics


def test_calculate_holds_breaks():
    """Test holds and breaks calculation."""
    events = [
        {"type": "pull", "point": 1, "team_id": "home", "elapsed_seconds": 0, "data": {"pullingTeamId": "home"}},
        {"type": "goal", "point": 1, "team_id": "away", "elapsed_seconds": 45, "data": {}},
        {"type": "pull", "point": 2, "team_id": "away", "elapsed_seconds": 60, "data": {"pullingTeamId": "away"}},
        {"type": "goal", "point": 2, "team_id": "home", "elapsed_seconds": 105, "data": {}},
    ]
    
    calc = MatchStatistics(events, "home", "away")
    result = calc.calculate_holds_breaks()
    
    # Point 1: home pulls (on defense), away scores = break for away
    assert result["away"]["breaks"] == 1
    assert result["home"]["breaks"] == 0
    
    # Point 2: away pulls (on defense), home scores = break for home
    assert result["home"]["breaks"] == 1
    assert result["away"]["holds"] == 0


def test_calculate_possession():
    """Test possession percentage calculation."""
    events = [
        {"type": "pull", "point": 1, "team_id": "home", "elapsed_seconds": 0, "data": {"pullingTeamId": "home"}},
        {"type": "turnover", "point": 1, "team_id": "away", "elapsed_seconds": 30, "data": {"turnoverType": "throwaway"}},
        {"type": "goal", "point": 1, "team_id": "home", "elapsed_seconds": 60, "data": {}},
    ]
    
    calc = MatchStatistics(events, "home", "away")
    result = calc.calculate_possession()
    
    # Away had possession 0-30s (30s)
    # Home had possession 30-60s (30s)
    # Should be roughly 50/50
    assert 45 <= result["home"] <= 55
    assert 45 <= result["away"] <= 55


def test_calculate_player_stats():
    """Test player statistics calculation."""
    events = [
        {
            "type": "goal",
            "point": 1,
            "player_id": "p1",
            "elapsed_seconds": 45,
            "data": {
                "scorerId": "p1",
                "assisterId": "p2",
                "offensiveLine": ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]
            }
        },
        {
            "type": "turnover",
            "point": 2,
            "player_id": "p3",
            "elapsed_seconds": 90,
            "data": {
                "turnoverType": "block",
                "causedById": "p8"
            }
        },
    ]
    
    calc = MatchStatistics(events, "home", "away")
    result = calc.calculate_player_stats()
    
    # Player p1 scored a goal
    assert result["p1"]["goals"] == 1
    
    # Player p2 had an assist
    assert result["p2"]["assists"] == 1
    
    # Player p8 had a block
    assert result["p8"]["blocks"] == 1
    
    # Player p3 had a turnover
    assert result["p3"]["turnovers"] == 1


def test_calculate_turnovers():
    """Test turnover counting by type."""
    events = [
        {"type": "turnover", "point": 1, "team_id": "home", "elapsed_seconds": 30, "data": {"turnoverType": "throwaway"}},
        {"type": "turnover", "point": 1, "team_id": "home", "elapsed_seconds": 45, "data": {"turnoverType": "drop"}},
        {"type": "turnover", "point": 2, "team_id": "away", "elapsed_seconds": 90, "data": {"turnoverType": "block"}},
    ]
    
    calc = MatchStatistics(events, "home", "away")
    result = calc.calculate_turnovers()
    
    assert result["home"]["throwaway"] == 1
    assert result["home"]["drop"] == 1
    assert result["away"]["block"] == 1


def test_offensive_efficiency():
    """Test offensive efficiency calculation."""
    events = [
        # Point 1: home has possession, scores (hold)
        {"type": "pull", "point": 1, "team_id": "away", "elapsed_seconds": 0, "data": {"pullingTeamId": "away"}},
        {"type": "goal", "point": 1, "team_id": "home", "elapsed_seconds": 45, "data": {}},
        
        # Point 2: away has possession, scores (hold)
        {"type": "pull", "point": 2, "team_id": "home", "elapsed_seconds": 60, "data": {"pullingTeamId": "home"}},
        {"type": "goal", "point": 2, "team_id": "away", "elapsed_seconds": 105, "data": {}},
        
        # Point 3: home has possession, away scores (break)
        {"type": "pull", "point": 3, "team_id": "away", "elapsed_seconds": 120, "data": {"pullingTeamId": "away"}},
        {"type": "goal", "point": 3, "team_id": "away", "elapsed_seconds": 165, "data": {}},
    ]
    
    calc = MatchStatistics(events, "home", "away")
    result = calc.calculate_team_stats()
    
    # Home: 1 hold, 0 breaks; Away: 1 break against home
    # Home efficiency: 1 / (1 + 1) = 0.5
    assert result["home"]["holds"] == 1
    assert result["home"]["breaks"] == 0
    assert result["home"]["offensive_efficiency"] == 0.5
    
    # Away: 1 hold, 1 break
    assert result["away"]["holds"] == 1
    assert result["away"]["breaks"] == 1

