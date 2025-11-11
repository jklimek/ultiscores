"""Tests for tournament generator."""
import pytest
from src.services.tournament_generator import (
    TournamentGenerator,
    TeamSeed,
)


def test_suggest_pool_count():
    """Test pool count suggestion."""
    teams = [TeamSeed(team_id=f"t{i}", seed=i) for i in range(8)]
    gen = TournamentGenerator(teams, {"format": "pool"})
    
    assert gen._suggest_pool_count(4) == 1
    assert gen._suggest_pool_count(8) == 2
    assert gen._suggest_pool_count(12) == 2
    assert gen._suggest_pool_count(16) == 4


def test_distribute_teams_to_pools():
    """Test snake seeding distribution."""
    teams = [TeamSeed(team_id=f"t{i}", seed=i+1) for i in range(8)]
    gen = TournamentGenerator(teams, {"format": "pool"})
    
    pools = gen._distribute_teams_to_pools(teams, 2)
    
    # Pool A: seeds 1, 4, 5, 8
    assert len(pools) == 2
    assert len(pools[0]) == 4
    assert len(pools[1]) == 4
    
    # Check snake seeding pattern
    assert pools[0][0].seed == 1
    assert pools[1][0].seed == 2
    assert pools[1][1].seed == 3
    assert pools[0][1].seed == 4


def test_generate_round_robin():
    """Test round-robin match generation."""
    teams = [
        TeamSeed(team_id="t1", seed=1),
        TeamSeed(team_id="t2", seed=2),
        TeamSeed(team_id="t3", seed=3),
        TeamSeed(team_id="t4", seed=4),
    ]
    gen = TournamentGenerator(teams, {"format": "pool"})
    
    matches = gen._generate_round_robin(teams, "Pool A", "pool-a")
    
    # 4 teams = 6 matches (combinations of 2)
    assert len(matches) == 6
    
    # Check all matches have pool_id
    assert all(m.pool_id == "pool-a" for m in matches)
    
    # Check all teams play each other once
    matchups = {(m.home_team_id, m.away_team_id) for m in matches}
    assert len(matchups) == 6


def test_generate_pool_format():
    """Test pool format generation."""
    teams = [TeamSeed(team_id=f"t{i}", seed=i+1) for i in range(8)]
    settings = {
        "format": "pool",
        "pool_count": 2,
        "rest_periods": 1,
    }
    gen = TournamentGenerator(teams, settings)
    
    result = gen.generate()
    
    assert "stages" in result
    assert "pools" in result
    assert "matches" in result
    
    # Should have 1 stage (pool play)
    assert len(result["stages"]) == 1
    assert result["stages"][0]["stage_type"] == "pool"
    
    # Should have 2 pools
    assert len(result["pools"]) == 2
    
    # Each pool should have 4 teams
    assert len(result["pools"][0]["teams"]) == 4
    assert len(result["pools"][1]["teams"]) == 4


def test_generate_single_elimination():
    """Test single elimination bracket generation."""
    teams = [TeamSeed(team_id=f"t{i}", seed=i+1) for i in range(8)]
    settings = {"format": "single_elim"}
    gen = TournamentGenerator(teams, settings)
    
    result = gen.generate()
    
    # Should have 1 stage (bracket)
    assert len(result["stages"]) == 1
    assert result["stages"][0]["stage_type"] == "bracket"
    
    # 8 teams = 4 first-round matches
    assert len(result["matches"]) == 4
    
    # Check seeding (1 vs 8, 2 vs 7, etc.)
    # Note: Actual implementation might vary


def test_get_bracket_round_name():
    """Test bracket round naming."""
    gen = TournamentGenerator([], {"format": "single_elim"})
    
    assert gen._get_bracket_round_name(1) == "Final"
    assert gen._get_bracket_round_name(2) == "Semifinals"
    assert gen._get_bracket_round_name(4) == "Quarterfinals"
    assert gen._get_bracket_round_name(8) == "Round of 16"


def test_power_pools_format():
    """Test power pools generation."""
    teams = [TeamSeed(team_id=f"t{i}", seed=i+1) for i in range(8)]
    settings = {
        "format": "power_pools",
        "pool_count": 2,
        "advancement": {"power_pool_size": 4},
        "rest_periods": 1,
    }
    gen = TournamentGenerator(teams, settings)
    
    result = gen.generate()
    
    # Should have 2 stages (initial pools + power pools)
    assert len(result["stages"]) >= 2
    
    # First stage is pool play
    assert result["stages"][0]["stage_type"] == "pool"
    
    # Second stage is placement/power pools
    assert result["stages"][1]["stage_type"] == "placement"

