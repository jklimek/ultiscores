import {
  type ApiClient,
  type ListMatchesParams,
  type ListPlayersParams,
  type ListTeamsParams,
  type ListTournamentsParams,
} from "@/lib/api/client";
import { mockData } from "@/lib/api/mock-data";

function filterByDivision<T extends { division?: string }>(
  collection: T[],
  division?: string,
) {
  if (!division) {
    return collection;
  }
  return collection.filter((item) => item.division === division);
}

export function createMockApiClient(): ApiClient {
  return {
    async listSeasons() {
      return mockData.seasons;
    },

    async listTournaments(params: ListTournamentsParams = {}) {
      let tournaments = [...mockData.tournaments];

      tournaments = filterByDivision(tournaments, params.division);

      if (params.seasonId) {
        tournaments = tournaments.filter(
          (tournament) => tournament.season === params.seasonId,
        );
      }

      if (params.status) {
        tournaments = tournaments.filter(
          (tournament) => tournament.status === params.status,
        );
      }

      if (params.search) {
        const q = params.search.toLowerCase();
        tournaments = tournaments.filter((tournament) =>
          tournament.name.toLowerCase().includes(q),
        );
      }

      return tournaments;
    },

    async getTournament(tournamentId: string) {
      const tournament = mockData.tournaments.find(
        (item) => item.id === tournamentId || item.slug === tournamentId,
      );
      if (!tournament) {
        throw new Error(`Tournament ${tournamentId} not found`);
      }
      return tournament;
    },

    async listMatches(params: ListMatchesParams = {}) {
      let matches = [...mockData.matches];
      if (params.tournamentId) {
        matches = matches.filter(
          (match) => match.tournamentId === params.tournamentId,
        );
      }
      if (params.teamId) {
        matches = matches.filter(
          (match) =>
            match.home.teamId === params.teamId ||
            match.away.teamId === params.teamId,
        );
      }
      if (params.division) {
        matches = matches.filter((match) => match.division === params.division);
      }
      if (params.status) {
        matches = matches.filter((match) => match.status === params.status);
      }
      return matches;
    },

    async getMatch(matchId: string) {
      const match = mockData.matches.find(
        (item) => item.id === matchId || item.slug === matchId,
      );
      if (!match) {
        throw new Error(`Match ${matchId} not found`);
      }
      return match;
    },

    async listMatchEvents(matchId: string) {
      const match = mockData.matches.find(
        (item) => item.id === matchId || item.slug === matchId,
      );
      if (!match) {
        throw new Error(`Match ${matchId} not found`);
      }
      return match.events;
    },

    async listSpiritScores(tournamentId: string) {
      const matchIds = mockData.matches
        .filter((match) => match.tournamentId === tournamentId)
        .map((match) => match.id);

      return mockData.spiritScores.filter((score) =>
        matchIds.includes(score.matchId),
      );
    },

    async listTeams(params: ListTeamsParams = {}) {
      let teams = [...mockData.teams];
      teams = filterByDivision(teams, params.division);
      if (params.seasonId) {
        teams = teams.filter((team) =>
          team.seasons.some((season) => season.season === params.seasonId),
        );
      }
      if (params.search) {
        const q = params.search.toLowerCase();
        teams = teams.filter(
          (team) =>
            team.name.toLowerCase().includes(q) ||
            team.city?.toLowerCase().includes(q),
        );
      }
      return teams;
    },

    async getTeam(teamId: string) {
      const team = mockData.teams.find(
        (item) => item.id === teamId || item.slug === teamId,
      );
      if (!team) {
        throw new Error(`Team ${teamId} not found`);
      }
      return team;
    },

    async listPlayers(params: ListPlayersParams = {}) {
      let players = [...mockData.players];
      if (params.teamId) {
        const rosterIds = mockData.teams
          .find((team) => team.id === params.teamId || team.slug === params.teamId)
          ?.roster.map((entry) => entry.player.id);
        if (rosterIds) {
          players = players.filter((player) => rosterIds.includes(player.id));
        }
      }
      if (params.tournamentId) {
        const rosterIds = mockData.teams.flatMap((team) =>
          team.roster
            .filter((roster) => roster.tournamentId === params.tournamentId)
            .map((roster) => roster.player.id),
        );
        players = players.filter((player) => rosterIds.includes(player.id));
      }
      if (params.search) {
        const q = params.search.toLowerCase();
        players = players.filter((player) =>
          player.name.display.toLowerCase().includes(q),
        );
      }
      return players;
    },

    async getPlayer(playerId: string) {
      const player = mockData.players.find((item) => item.id === playerId);
      if (!player) {
        throw new Error(`Player ${playerId} not found`);
      }
      return player;
    },
  };
}

export { createApiClient } from "@/lib/api/client";

