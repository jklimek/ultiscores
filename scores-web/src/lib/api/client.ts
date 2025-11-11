import { z } from "zod";

import { apiFetch } from "@/lib/api/http";
import {
  matchEventSchema,
  matchSchema,
  matchSummarySchema,
  playerSchema,
  seasonSummarySchema,
  spiritScoreSchema,
  teamSchema,
  tournamentSchema,
  type Division,
  type Match,
  type MatchEvent,
  type Player,
  type SeasonSummary,
  type SpiritScore,
  type Team,
  type Tournament,
} from "@/lib/api/schemas";

// FastAPI returns arrays directly for collections (not wrapped in data/meta)
const collectionResponse = <T extends z.ZodTypeAny>(schema: T) =>
  z.array(schema);

// FastAPI returns entities directly (not wrapped in data)
const entityResponse = <T extends z.ZodTypeAny>(schema: T) => schema;

type DivisionFilter = {
  division?: Division;
};

export type ListTournamentsParams = DivisionFilter & {
  seasonId?: string;
  status?: "upcoming" | "in_progress" | "completed" | "cancelled";
  search?: string;
};

export type ListMatchesParams = DivisionFilter & {
  tournamentId?: string;
  teamId?: string;
  status?: "scheduled" | "live" | "final";
};

export type ListTeamsParams = DivisionFilter & {
  seasonId?: string;
  search?: string;
};

export type ListPlayersParams = {
  teamId?: string;
  tournamentId?: string;
  search?: string;
};

const tournamentCollectionSchema = collectionResponse(tournamentSchema);
const matchCollectionSchema = collectionResponse(matchSummarySchema);  // Use matchSummarySchema for list
const matchEventCollectionSchema = collectionResponse(matchEventSchema);
const teamCollectionSchema = collectionResponse(teamSchema);
const playerCollectionSchema = collectionResponse(playerSchema);
const seasonCollectionSchema = collectionResponse(seasonSummarySchema);
const spiritCollectionSchema = collectionResponse(spiritScoreSchema);

function buildQueryString(
  params: Record<string, string | number | undefined>,
): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, String(value));
    }
  });
  const qs = searchParams.toString();
  return qs ? `?${qs}` : "";
}

export interface ApiClient {
  listSeasons(): Promise<SeasonSummary[]>;
  listTournaments(params?: ListTournamentsParams): Promise<Tournament[]>;
  getTournament(tournamentId: string): Promise<Tournament>;

  listMatches(params?: ListMatchesParams): Promise<Match[]>;
  getMatch(matchId: string): Promise<Match>;
  listMatchEvents(matchId: string): Promise<MatchEvent[]>;

  listSpiritScores(tournamentId: string): Promise<SpiritScore[]>;

  listTeams(params?: ListTeamsParams): Promise<Team[]>;
  getTeam(teamId: string): Promise<Team>;

  listPlayers(params?: ListPlayersParams): Promise<Player[]>;
  getPlayer(playerId: string): Promise<Player>;
}

export function createApiClient(): ApiClient {
  return {
    async listSeasons() {
      const response = await apiFetch(
        "/v1/seasons/",
        seasonCollectionSchema,
        { revalidate: 3600 },
      );
      return response;
    },

    async listTournaments(params = {}) {
      const query = buildQueryString({
        seasonId: params.seasonId,
        division: params.division,
        status: params.status,
        search: params.search,
      });

      const response = await apiFetch(
        `/v1/tournaments/${query}`,
        tournamentCollectionSchema,
        { revalidate: params.status === "in_progress" ? 30 : 600 },
      );
      return response;
    },

    async getTournament(tournamentId: string) {
      const response = await apiFetch(
        `/v1/tournaments/${tournamentId}`,
        entityResponse(tournamentSchema),
        { revalidate: 30 },
      );
      return response;
    },

    async listMatches(params = {}) {
      const query = buildQueryString({
        tournamentId: params.tournamentId,
        teamId: params.teamId,
        division: params.division,
        status: params.status,
      });

      const response = await apiFetch(
        `/v1/matches/${query}`,
        matchCollectionSchema,
        { revalidate: params.status === "live" ? 15 : 120 },
      );
      return response;
    },

    async getMatch(matchId: string) {
      const response = await apiFetch(
        `/v1/matches/${matchId}`,
        entityResponse(matchSchema),
        { revalidate: 10 },
      );
      return response;
    },

    async listMatchEvents(matchId: string) {
      const response = await apiFetch(
        `/v1/matches/${matchId}/events`,
        matchEventCollectionSchema,
        { revalidate: 10 },
      );
      return response;
    },

    async listSpiritScores(tournamentId: string) {
      const response = await apiFetch(
        `/v1/tournaments/${tournamentId}/spirit`,
        spiritCollectionSchema,
        { revalidate: 600 },
      );
      return response;
    },

    async listTeams(params = {}) {
      const query = buildQueryString({
        seasonId: params.seasonId,
        division: params.division,
        search: params.search,
      });

      const response = await apiFetch(
        `/v1/teams/${query}`,
        teamCollectionSchema,
        { revalidate: 1800 },
      );
      return response;
    },

    async getTeam(teamId: string) {
      const response = await apiFetch(
        `/v1/teams/${teamId}`,
        entityResponse(teamSchema),
        { revalidate: 600 },
      );
      return response;
    },

    async listPlayers(params = {}) {
      const query = buildQueryString({
        teamId: params.teamId,
        tournamentId: params.tournamentId,
        search: params.search,
      });

      const response = await apiFetch(
        `/v1/players/${query}`,
        playerCollectionSchema,
        { revalidate: 1800 },
      );
      return response;
    },

    async getPlayer(playerId: string) {
      const response = await apiFetch(
        `/v1/players/${playerId}`,
        entityResponse(playerSchema),
        { revalidate: 1800 },
      );
      return response;
    },
  };
}

export type {
  Match,
  MatchEvent,
  Player,
  SeasonSummary,
  SpiritScore,
  Team,
  Tournament,
  Division,
};

