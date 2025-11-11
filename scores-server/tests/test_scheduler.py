"""Tests for match scheduler."""
import pytest
from datetime import datetime, timedelta
from src.services.scheduler import MatchScheduler


def test_schedule_matches_basic():
    """Test basic match scheduling."""
    start_time = datetime(2025, 9, 13, 9, 0)
    scheduler = MatchScheduler(
        start_time=start_time,
        field_count=2,
        match_duration_minutes=75,
        turnaround_minutes=15,
        rest_periods=1
    )
    
    matches = [
        {"match_id": "m1", "home_team_id": "t1", "away_team_id": "t2"},
        {"match_id": "m2", "home_team_id": "t3", "away_team_id": "t4"},
        {"match_id": "m3", "home_team_id": "t1", "away_team_id": "t3"},
    ]
    
    scheduled = scheduler.schedule_matches(matches)
    
    # Should schedule all 3 matches
    assert len(scheduled) == 3
    
    # First two matches can start simultaneously
    assert scheduled[0].start_time == start_time
    assert scheduled[1].start_time == start_time
    
    # Different fields
    assert scheduled[0].field_id != scheduled[1].field_id


def test_rest_periods():
    """Test that teams get rest periods between matches."""
    start_time = datetime(2025, 9, 13, 9, 0)
    scheduler = MatchScheduler(
        start_time=start_time,
        field_count=1,
        match_duration_minutes=60,
        turnaround_minutes=10,
        rest_periods=1  # At least 1 match break
    )
    
    matches = [
        {"match_id": "m1", "home_team_id": "t1", "away_team_id": "t2"},
        {"match_id": "m2", "home_team_id": "t3", "away_team_id": "t4"},
        {"match_id": "m3", "home_team_id": "t1", "away_team_id": "t3"},  # t1 plays again
    ]
    
    scheduled = scheduler.schedule_matches(matches)
    
    # m1 and m2 should be scheduled first
    # m3 should wait until after m2 (so t1 gets a break)
    assert scheduled[0].match_id == "m1"
    assert scheduled[1].match_id == "m2"
    assert scheduled[2].match_id == "m3"
    
    # m3 should start after m2 finishes
    m2_end = scheduled[1].start_time + timedelta(minutes=60 + 10)
    assert scheduled[2].start_time >= m2_end


def test_field_allocation():
    """Test field allocation balancing."""
    start_time = datetime(2025, 9, 13, 9, 0)
    scheduler = MatchScheduler(
        start_time=start_time,
        field_count=2,
        match_duration_minutes=60,
        turnaround_minutes=10,
        rest_periods=0
    )
    
    matches = [
        {"match_id": f"m{i}", "home_team_id": f"t{i*2}", "away_team_id": f"t{i*2+1}"}
        for i in range(6)
    ]
    
    scheduled = scheduler.schedule_matches(matches)
    
    # Count matches per field
    field1_count = sum(1 for m in scheduled if m.field_id == "field-1")
    field2_count = sum(1 for m in scheduled if m.field_id == "field-2")
    
    # Should be balanced (3 each)
    assert field1_count == 3
    assert field2_count == 3


def test_get_schedule_summary():
    """Test schedule summary generation."""
    start_time = datetime(2025, 9, 13, 9, 0)
    scheduler = MatchScheduler(
        start_time=start_time,
        field_count=2,
        match_duration_minutes=60,
        turnaround_minutes=10,
        rest_periods=0
    )
    
    matches = [
        {"match_id": "m1", "home_team_id": "t1", "away_team_id": "t2"},
        {"match_id": "m2", "home_team_id": "t3", "away_team_id": "t4"},
    ]
    
    scheduler.schedule_matches(matches)
    summary = scheduler.get_schedule_summary()
    
    assert summary["total_matches"] == 2
    assert summary["fields_used"] == 2
    assert "start_time" in summary
    assert "end_time" in summary
    assert "total_duration_hours" in summary


def test_multiple_rest_periods():
    """Test scheduling with 2 rest periods."""
    start_time = datetime(2025, 9, 13, 9, 0)
    scheduler = MatchScheduler(
        start_time=start_time,
        field_count=1,
        match_duration_minutes=60,
        turnaround_minutes=10,
        rest_periods=2  # Team must sit out 2 matches
    )
    
    matches = [
        {"match_id": "m1", "home_team_id": "t1", "away_team_id": "t2"},
        {"match_id": "m2", "home_team_id": "t3", "away_team_id": "t4"},
        {"match_id": "m3", "home_team_id": "t5", "away_team_id": "t6"},
        {"match_id": "m4", "home_team_id": "t1", "away_team_id": "t3"},  # t1 and t3 play again
    ]
    
    scheduled = scheduler.schedule_matches(matches)
    
    # m4 should be scheduled after m1, m2, and m3
    assert scheduled[3].match_id == "m4"
    
    # Verify t1 had 2 matches of rest
    # (played m1, sat out m2 and m3, then played m4)

