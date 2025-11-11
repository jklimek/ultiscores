"""Tournament generator supporting various formats.

Formats:
- Pool play with round-robin
- Swiss system
- Power pools (top teams advance to championship pool)
- Cross-matches between pools
- Single/double elimination playoffs
"""
import uuid
import math
from typing import List, Dict, Tuple, Optional, Any
from itertools import combinations
from dataclasses import dataclass


@dataclass
class TeamSeed:
    """Team with seed."""
    team_id: str
    seed: int


@dataclass
class GeneratedMatch:
    """Generated match."""
    home_team_id: str
    away_team_id: str
    round: str
    pool_id: Optional[str] = None
    field_id: Optional[str] = None
    start_time: Optional[str] = None


class TournamentGenerator:
    """Generate tournament structure and matches."""
    
    def __init__(self, teams: List[TeamSeed], settings: Dict[str, Any]):
        """
        Initialize generator.
        
        Args:
            teams: List of teams with seeds
            settings: Tournament settings
        """
        self.teams = sorted(teams, key=lambda t: t.seed)
        self.settings = settings
        self.format = settings.get("format", "power_pools")
        
    def generate(self) -> Dict[str, Any]:
        """
        Generate full tournament structure.
        
        Returns:
            {
                "stages": [...],
                "pools": [...],
                "matches": [...]
            }
        """
        if self.format == "swiss":
            return self.generate_swiss()
        elif self.format == "single_elim":
            return self.generate_single_elimination()
        elif self.format == "double_elim":
            return self.generate_double_elimination()
        elif self.format in ["pool", "power_pools"]:
            return self.generate_pool_format()
        else:
            raise ValueError(f"Unknown format: {self.format}")
    
    def generate_pool_format(self) -> Dict[str, Any]:
        """Generate pool play with optional power pools."""
        stages = []
        pools = []
        matches = []
        
        # Calculate pool structure
        pool_count = self.settings.get("pool_count")
        if not pool_count:
            pool_count = self._suggest_pool_count(len(self.teams))
        
        # Create initial pools
        initial_pools = self._distribute_teams_to_pools(self.teams, pool_count)
        
        # Stage 1: Initial pool play
        stage1_id = str(uuid.uuid4())
        stages.append({
            "id": stage1_id,
            "name": "Pool Play",
            "stage_type": "pool",
            "order": 0,
        })
        
        for i, pool_teams in enumerate(initial_pools):
            pool_id = str(uuid.uuid4())
            pool_label = chr(65 + i)  # A, B, C, ...
            
            pools.append({
                "id": pool_id,
                "stage_id": stage1_id,
                "label": f"Pool {pool_label}",
                "teams": [{"team_id": t.team_id, "seed": t.seed} for t in pool_teams],
            })
            
            # Generate round-robin matches within pool
            pool_matches = self._generate_round_robin(pool_teams, f"Pool {pool_label}", pool_id)
            matches.extend(pool_matches)
        
        # Power pools or cross-matches
        if self.format == "power_pools":
            advancement = self.settings.get("advancement", {})
            power_pool_size = advancement.get("power_pool_size", 4)
            
            # Stage 2: Power pools
            stage2_id = str(uuid.uuid4())
            stages.append({
                "id": stage2_id,
                "name": "Championship Pool",
                "stage_type": "placement",
                "order": 1,
            })
            
            # Championship pool (top N from each pool)
            champ_pool_id = str(uuid.uuid4())
            pools.append({
                "id": champ_pool_id,
                "stage_id": stage2_id,
                "label": "Championship Pool",
                "teams": [],  # Will be filled based on pool results
            })
            
            # Consolation pool
            if len(self.teams) > power_pool_size:
                consol_pool_id = str(uuid.uuid4())
                pools.append({
                    "id": consol_pool_id,
                    "stage_id": stage2_id,
                    "label": "Consolation Pool",
                    "teams": [],
                })
        
        # Cross-matches if specified
        cross_matches = self.settings.get("advancement", {}).get("cross_matches", [])
        if cross_matches and pool_count >= 2:
            stage3_id = str(uuid.uuid4())
            stages.append({
                "id": stage3_id,
                "name": "Placement Matches",
                "stage_type": "placement",
                "order": 2,
            })
            
            # Generate cross-matches (e.g., A2 vs B2)
            # Note: These would be scheduled after pool play
            # Actual teams TBD based on standings
        
        return {
            "stages": stages,
            "pools": pools,
            "matches": matches,
        }
    
    def generate_swiss(self) -> Dict[str, Any]:
        """Generate Swiss system tournament."""
        stages = []
        matches = []
        
        rounds = self.settings.get("rounds") or math.ceil(math.log2(len(self.teams)))
        
        stage_id = str(uuid.uuid4())
        stages.append({
            "id": stage_id,
            "name": "Swiss Rounds",
            "stage_type": "swiss",
            "order": 0,
        })
        
        # Initial round: pair by seeds (1v2, 3v4, etc.)
        for i in range(0, len(self.teams) - 1, 2):
            matches.append(GeneratedMatch(
                home_team_id=self.teams[i].team_id,
                away_team_id=self.teams[i + 1].team_id,
                round="Round 1",
            ))
        
        # Subsequent rounds would be generated based on results
        # For now, generate placeholder structure
        for round_num in range(2, rounds + 1):
            # Matches will be generated after previous round results
            pass
        
        return {
            "stages": stages,
            "pools": [],
            "matches": matches,
        }
    
    def generate_single_elimination(self) -> Dict[str, Any]:
        """Generate single elimination bracket."""
        stages = []
        matches = []
        
        stage_id = str(uuid.uuid4())
        stages.append({
            "id": stage_id,
            "name": "Playoffs",
            "stage_type": "bracket",
            "order": 0,
        })
        
        # Calculate bracket size (next power of 2)
        bracket_size = 2 ** math.ceil(math.log2(len(self.teams)))
        
        # Generate bracket pairings (1 vs bracket_size, 2 vs bracket_size-1, etc.)
        round_name = self._get_bracket_round_name(bracket_size // 2)
        
        for i in range(bracket_size // 2):
            high_seed = i
            low_seed = bracket_size - 1 - i
            
            if high_seed < len(self.teams) and low_seed < len(self.teams):
                matches.append(GeneratedMatch(
                    home_team_id=self.teams[high_seed].team_id,
                    away_team_id=self.teams[low_seed].team_id,
                    round=round_name,
                ))
            elif high_seed < len(self.teams):
                # Bye for high seed (advances automatically)
                pass
        
        return {
            "stages": stages,
            "pools": [],
            "matches": matches,
        }
    
    def generate_double_elimination(self) -> Dict[str, Any]:
        """Generate double elimination bracket."""
        # Similar to single elimination but with winner's and loser's brackets
        stages = []
        matches = []
        
        stage_id = str(uuid.uuid4())
        stages.append({
            "id": stage_id,
            "name": "Playoffs",
            "stage_type": "bracket",
            "order": 0,
        })
        
        # Generate initial winner's bracket (same as single elim)
        bracket_size = 2 ** math.ceil(math.log2(len(self.teams)))
        round_name = self._get_bracket_round_name(bracket_size // 2)
        
        for i in range(bracket_size // 2):
            high_seed = i
            low_seed = bracket_size - 1 - i
            
            if high_seed < len(self.teams) and low_seed < len(self.teams):
                matches.append(GeneratedMatch(
                    home_team_id=self.teams[high_seed].team_id,
                    away_team_id=self.teams[low_seed].team_id,
                    round=f"Winner's {round_name}",
                ))
        
        # Loser's bracket would be generated as teams drop from winner's bracket
        
        return {
            "stages": stages,
            "pools": [],
            "matches": matches,
        }
    
    def _suggest_pool_count(self, team_count: int) -> int:
        """Suggest optimal number of pools."""
        if team_count <= 6:
            return 1
        elif team_count <= 12:
            return 2
        elif team_count <= 20:
            return 4
        else:
            return 6
    
    def _distribute_teams_to_pools(
        self, teams: List[TeamSeed], pool_count: int
    ) -> List[List[TeamSeed]]:
        """
        Distribute teams to pools using snake seeding.
        
        Snake seeding example for 2 pools:
        Pool A: 1, 4, 5, 8
        Pool B: 2, 3, 6, 7
        """
        pools = [[] for _ in range(pool_count)]
        
        for i, team in enumerate(teams):
            pool_idx = i % (2 * pool_count)
            if pool_idx >= pool_count:
                # Snake back
                pool_idx = 2 * pool_count - pool_idx - 1
            pools[pool_idx].append(team)
        
        return pools
    
    def _generate_round_robin(
        self, teams: List[TeamSeed], round_name: str, pool_id: str
    ) -> List[GeneratedMatch]:
        """Generate round-robin matches for a pool."""
        matches = []
        
        # Generate all possible pairings
        for home, away in combinations(teams, 2):
            matches.append(GeneratedMatch(
                home_team_id=home.team_id,
                away_team_id=away.team_id,
                round=round_name,
                pool_id=pool_id,
            ))
        
        return matches
    
    def _get_bracket_round_name(self, matches_in_round: int) -> str:
        """Get name for bracket round."""
        if matches_in_round == 1:
            return "Final"
        elif matches_in_round == 2:
            return "Semifinals"
        elif matches_in_round == 4:
            return "Quarterfinals"
        elif matches_in_round == 8:
            return "Round of 16"
        else:
            return f"Round of {matches_in_round * 2}"


async def generate_tournament_structure(
    tournament_id: str,
    teams: List[Dict],
    settings: Dict[str, Any],
    db
) -> Dict[str, Any]:
    """
    Generate tournament structure and save to database.
    
    Args:
        tournament_id: Tournament ID
        teams: List of teams with seeds
        settings: Tournament settings
        db: Database session
        
    Returns:
        Generated structure
    """
    from src.models import Stage, Pool, Match
    
    # Convert teams to TeamSeed objects
    team_seeds = [TeamSeed(team_id=t["team_id"], seed=t["seed"]) for t in teams]
    
    # Generate structure
    generator = TournamentGenerator(team_seeds, settings)
    structure = generator.generate()
    
    # Save stages
    for stage_data in structure["stages"]:
        stage = Stage(
            id=stage_data["id"],
            tournament_id=tournament_id,
            name=stage_data["name"],
            stage_type=stage_data["stage_type"],
            division=settings.get("division", "mixed"),
            order=stage_data["order"],
        )
        db.add(stage)
    
    # Save pools
    for pool_data in structure["pools"]:
        pool = Pool(
            id=pool_data["id"],
            stage_id=pool_data["stage_id"],
            label=pool_data["label"],
            teams=pool_data["teams"],
        )
        db.add(pool)
    
    # Save matches (will be scheduled separately)
    for i, match_data in enumerate(structure["matches"]):
        match = Match(
            id=str(uuid.uuid4()),
            slug=f"match-{i + 1}",
            tournament_id=tournament_id,
            stage_id=structure["stages"][0]["id"],
            pool_id=match_data.pool_id,
            division=settings.get("division", "mixed"),
            round=match_data.round,
            home_team_id=match_data.home_team_id,
            away_team_id=match_data.away_team_id,
            start_time="",  # Will be set by scheduler
            status="scheduled",
        )
        db.add(match)
    
    await db.commit()
    
    return structure

