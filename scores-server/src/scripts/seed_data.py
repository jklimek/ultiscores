"""Seed database with Polish Ultimate Frisbee data."""
import asyncio
import uuid
from datetime import datetime, timedelta

from src.database import AsyncSessionLocal
from src.models import (
    Season, Team, Player, Venue, Tournament, Stage, Pool,
    Match, TournamentRoster
)


async def seed_database():
    """Seed database with sample data."""
    async with AsyncSessionLocal() as session:
        try:
            print("Starting database seeding...")
            
            # Create season
            season = Season(
                id="2025",
                label="2025",
                year=2025
            )
            session.add(season)
            
            # Create venue
            venue = Venue(
                id="orlik-warsaw",
                name="Orlik Mokotów",
                city="Warsaw",
                country="Poland",
                timezone="Europe/Warsaw",
                latitude=52.1876,
                longitude=21.0440,
                address="ul. Puławska 2, Warsaw",
                fields=[
                    {"id": "1", "label": "Field 1", "surface": "grass"},
                    {"id": "2", "label": "Field 2", "surface": "grass"},
                ]
            )
            session.add(venue)
            
            # Create teams
            teams_data = [
                {
                    "id": "sky-this", "name": "Sky This", "short_name": "Sky",
                    "slug": "sky-this", "city": "Warsaw", "division": "mixed",
                    "primary_color": "#0066CC", "secondary_color": "#FFFFFF"
                },
                {
                    "id": "4hands", "name": "4Hands", "short_name": "4H",
                    "slug": "4hands", "city": "Wrocław", "division": "mixed",
                    "primary_color": "#FF6600", "secondary_color": "#000000"
                },
                {
                    "id": "wroclaw-panthers", "name": "Wrocław Panthers", "short_name": "Panthers",
                    "slug": "wroclaw-panthers", "city": "Wrocław", "division": "mixed",
                    "primary_color": "#000000", "secondary_color": "#FFD700"
                },
                {
                    "id": "poznan-hussars", "name": "Poznań Hussars", "short_name": "Hussars",
                    "slug": "poznan-hussars", "city": "Poznań", "division": "mixed",
                    "primary_color": "#DC143C", "secondary_color": "#FFFFFF"
                },
                {
                    "id": "krakow-dragons", "name": "Kraków Dragons", "short_name": "Dragons",
                    "slug": "krakow-dragons", "city": "Kraków", "division": "mixed",
                    "primary_color": "#228B22", "secondary_color": "#FFD700"
                },
            ]
            
            teams = []
            for team_data in teams_data:
                team = Team(**team_data, country="Poland")
                session.add(team)
                teams.append(team)
            
            # Create players for Sky This
            players_sky = [
                {"id": "p1", "first_name": "Benedykt", "last_name": "Deskur", "nationality": "POL", "jersey": 47},
                {"id": "p2", "first_name": "Krzysztof", "last_name": "Litwiński", "nationality": "POL", "jersey": 29},
                {"id": "p3", "first_name": "Maciej", "last_name": "Litwiński", "nationality": "POL", "jersey": 63},
                {"id": "p4", "first_name": "Zuzanna", "last_name": "Madej", "nationality": "POL", "jersey": 16},
                {"id": "p5", "first_name": "Kinga", "last_name": "Szymczak", "nationality": "POL", "jersey": 3},
                {"id": "p6", "first_name": "Piotr", "last_name": "Janik", "nationality": "POL", "jersey": 20},
            ]
            
            # Create players for 4Hands
            players_4hands = [
                {"id": "p7", "first_name": "Piotr", "last_name": "Latoszewski", "nationality": "POL", "jersey": 31},
                {"id": "p8", "first_name": "Kamil", "last_name": "Osiecki", "nationality": "POL", "jersey": 16},
                {"id": "p9", "first_name": "Dorota", "last_name": "Stanisławska", "nationality": "POL", "jersey": 39},
                {"id": "p10", "first_name": "Grażyna", "last_name": "Chlebicka", "nationality": "POL", "jersey": 4},
                {"id": "p11", "first_name": "Julia", "last_name": "Urbańska", "nationality": "POL", "jersey": 5},
            ]
            
            all_players = players_sky + players_4hands
            
            for player_data in all_players:
                jersey = player_data.pop("jersey")
                player = Player(
                    **player_data,
                    roles=["handler", "cutter"],
                    dominant_positions=["offense", "defense"]
                )
                session.add(player)
            
            # Create tournament
            tournament = Tournament(
                id="mpx-2025",
                slug="mistrzostwa-polski-mixed-2025",
                name="Mistrzostwa Polski Mixed 2025",
                season_id=season.id,
                division="mixed",
                start_date="2025-09-13",
                end_date="2025-09-14",
                status="upcoming",
                venue_id=venue.id,
                organiser={"name": "PSGU", "website": "https://frisbee.pl"},
                settings={
                    "format": "power_pools",
                    "pool_count": 2,
                    "teams_per_pool": None,
                    "rest_periods": 1,
                    "match_duration_minutes": 75,
                    "field_count": 2,
                    "cap_at": 15,
                },
                teams=[
                    {"team_id": teams[0].id, "seed": 1},
                    {"team_id": teams[1].id, "seed": 2},
                    {"team_id": teams[2].id, "seed": 3},
                    {"team_id": teams[3].id, "seed": 4},
                    {"team_id": teams[4].id, "seed": 5},
                ]
            )
            session.add(tournament)
            
            # Create tournament rosters
            for i, player_data in enumerate(players_sky):
                roster = TournamentRoster(
                    id=str(uuid.uuid4()),
                    tournament_id=tournament.id,
                    team_id=teams[0].id,
                    player_id=player_data["id"],
                    jersey_number=all_players[i].get("jersey", i + 1),
                    is_captain=(i == 0)
                )
                session.add(roster)
            
            for i, player_data in enumerate(players_4hands):
                roster = TournamentRoster(
                    id=str(uuid.uuid4()),
                    tournament_id=tournament.id,
                    team_id=teams[1].id,
                    player_id=player_data["id"],
                    jersey_number=all_players[len(players_sky) + i].get("jersey", i + 1),
                    is_captain=(i == 0)
                )
                session.add(roster)
            
            # Create stages
            stage1 = Stage(
                id="stage1-mpx2025",
                tournament_id=tournament.id,
                name="Pool Play",
                stage_type="pool",
                division="mixed",
                order=0
            )
            session.add(stage1)
            
            stage2 = Stage(
                id="stage2-mpx2025",
                tournament_id=tournament.id,
                name="Playoffs",
                stage_type="bracket",
                division="mixed",
                order=1
            )
            session.add(stage2)
            
            # Create pools
            pool_a = Pool(
                id="pool-a-mpx2025",
                stage_id=stage1.id,
                label="Pool A",
                teams=[
                    {"team_id": teams[0].id, "seed": 1},
                    {"team_id": teams[2].id, "seed": 3},
                ]
            )
            session.add(pool_a)
            
            pool_b = Pool(
                id="pool-b-mpx2025",
                stage_id=stage1.id,
                label="Pool B",
                teams=[
                    {"team_id": teams[1].id, "seed": 2},
                    {"team_id": teams[3].id, "seed": 4},
                ]
            )
            session.add(pool_b)
            
            # Create sample matches
            match1 = Match(
                id="match1-mpx2025",
                slug="sky-this-vs-wroclaw-panthers",
                tournament_id=tournament.id,
                stage_id=stage1.id,
                pool_id=pool_a.id,
                division="mixed",
                round="Pool A",
                home_team_id=teams[0].id,
                away_team_id=teams[2].id,
                start_time=(datetime.now() + timedelta(days=1)).isoformat(),
                status="scheduled",
                field_id="1",
                field_label="Field 1",
            )
            session.add(match1)
            
            match2 = Match(
                id="match2-mpx2025",
                slug="4hands-vs-poznan-hussars",
                tournament_id=tournament.id,
                stage_id=stage1.id,
                pool_id=pool_b.id,
                division="mixed",
                round="Pool B",
                home_team_id=teams[1].id,
                away_team_id=teams[3].id,
                start_time=(datetime.now() + timedelta(days=1, hours=2)).isoformat(),
                status="scheduled",
                field_id="2",
                field_label="Field 2",
            )
            session.add(match2)
            
            # Final match (example)
            match_final = Match(
                id="match-final-mpx2025",
                slug="final-sky-this-vs-4hands",
                tournament_id=tournament.id,
                stage_id=stage2.id,
                pool_id=None,
                division="mixed",
                round="Final",
                home_team_id=teams[0].id,
                away_team_id=teams[1].id,
                start_time=(datetime.now() + timedelta(days=2)).isoformat(),
                status="scheduled",
                field_id="1",
                field_label="Field 1",
                home_score=13,
                away_score=10,
            )
            session.add(match_final)
            
            await session.commit()
            print("✅ Database seeded successfully!")
            print(f"- Created {len(teams_data)} teams")
            print(f"- Created {len(all_players)} players")
            print(f"- Created 1 tournament with {len([match1, match2, match_final])} matches")
            
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())

