import { z } from "zod";

export const divisionSchema = z.enum([
  "open",
  "women",
  "mixed",
  "junior",
  "masters",
]);

export const tournamentStatusSchema = z.enum([
  "upcoming",
  "in_progress",
  "completed",
  "cancelled",
]);

export const stageTypeSchema = z.enum([
  "round_robin",
  "pool",
  "bracket",
  "placement",
  "relegation",
]);

export const matchStatusSchema = z.enum([
  "scheduled",
  "live",
  "halftime",
  "final",
  "cancelled",
  "delayed",
]);

export const genderDivisionSchema = z.enum(["open", "women", "mixed"]);

export const turnoverTypeSchema = z.enum([
  "throwaway",
  "drop",
  "stall",
  "callahan",
  "block",
  "unknown",
]);

export const timeoutTypeSchema = z.enum(["team", "official", "spirit"]);

const personNameSchema = z.object({
  first: z.string(),
  last: z.string(),
  display: z.string(),
});

export const playerTeamHistorySchema = z.object({
  teamId: z.string(),
  teamName: z.string(),
  season: z.string(),
  division: divisionSchema,
  tournaments: z.array(
    z.object({
      tournamentId: z.string(),
      tournamentName: z.string(),
      placement: z.number().int().nullable(),
    }),
  ),
});

export const playerSchema = z.object({
  id: z.string(),
  jerseyNumber: z.number().int().nullable(),
  name: personNameSchema,
  pronouns: z.string().nullish(),
  nationality: z.string().nullish(),
  dateOfBirth: z.string().nullish(),
  heightCm: z.number().nullish(),
  roles: z.array(z.enum(["handler", "cutter", "flex"])).default([]),
  throws: z.enum(["left", "right", "both"]).nullish(),
  dominantPositions: z.array(z.string()).default([]),
  profileImageUrl: z.string().url().nullish(),
  clubHistory: z.array(playerTeamHistorySchema),
  stats: z
    .object({
      totalGoals: z.number().nonnegative(),
      totalAssists: z.number().nonnegative(),
      totalDs: z.number().nonnegative(),
      totalPointsPlayed: z.number().nonnegative(),
    })
    .nullish(),
});

export const teamSeasonSummarySchema = z.object({
  season: z.string(),
  division: divisionSchema,
  tournaments: z.array(
    z.object({
      tournamentId: z.string(),
      tournamentName: z.string(),
      placement: z.number().int().nullable(),
      wins: z.number().int(),
      losses: z.number().int(),
    }),
  ),
});

export const teamSchema = z.object({
  id: z.string(),
  name: z.string(),
  shortName: z.string(),
  slug: z.string(),
  division: divisionSchema,
  clubName: z.string().nullish(),
  city: z.string().nullish(),
  country: z.string().nullish(),
  foundedYear: z.number().int().nullish(),
  primaryColor: z.string().nullish(),
  secondaryColor: z.string().nullish(),
  crestUrl: z.string().url().nullish(),
  website: z.string().url().nullish(),
  seasons: z.array(teamSeasonSummarySchema),
  roster: z.array(
    z.object({
      tournamentId: z.string(),
      player: playerSchema,
      jerseyNumber: z.number().int().nullable(),
      captain: z.boolean().default(false),
    }),
  ),
});

export const venueSchema = z.object({
  name: z.string(),
  city: z.string(),
  country: z.string(),
  latitude: z.number().nullable(),
  longitude: z.number().nullable(),
  address: z.string().nullish(),
  timezone: z.string(),
  fields: z.array(
    z.object({
      id: z.string(),
      label: z.string(),
      surface: z.enum(["grass", "turf", "indoor", "sand"]).nullish(),
    }),
  ),
});

const baseMatchEventSchema = z.object({
  id: z.string(),
  sequence: z.number().int(),
  point: z.number().int(),
  elapsedSeconds: z.number().nonnegative(),
  clockLabel: z.string().nullable(),
  createdAt: z.string(),
  teamId: z.string().nullable(),
  summary: z.string().optional(),
});

const goalEventSchema = baseMatchEventSchema.extend({
  type: z.literal("goal"),
  scorerId: z.string(),
  assisterId: z.string().nullable(),
  offensiveLine: z.array(z.string()).default([]),
});

const turnoverEventSchema = baseMatchEventSchema.extend({
  type: z.literal("turnover"),
  turnoverType: turnoverTypeSchema,
  causedById: z.string().nullable(),
  reason: z.string().optional(),
});

const timeoutEventSchema = baseMatchEventSchema.extend({
  type: z.literal("timeout"),
  timeoutType: timeoutTypeSchema,
});

const callEventSchema = baseMatchEventSchema.extend({
  type: z.literal("call"),
  callType: z.enum(["foul", "travel", "pick", "injury", "other"]),
  resolved: z.boolean().default(true),
});

const pullEventSchema = baseMatchEventSchema.extend({
  type: z.literal("pull"),
  pullingTeamId: z.string(),
});

const periodEventSchema = baseMatchEventSchema.extend({
  type: z.literal("period"),
  label: z.string(),
});

export const matchEventSchema = z.discriminatedUnion("type", [
  goalEventSchema,
  turnoverEventSchema,
  timeoutEventSchema,
  callEventSchema,
  pullEventSchema,
  periodEventSchema,
]);

export const matchTeamStateSchema = z.object({
  teamId: z.string(),
  score: z.number().int(),
  timeoutsRemaining: z.number().int(),
  spiritScore: z.number().min(0).max(5).nullable(),
});

// Match summary schema for list endpoints (without events/stats/venue)
export const matchSummarySchema = z.object({
  id: z.string(),
  slug: z.string(),
  tournamentId: z.string(),
  division: divisionSchema,
  round: z.string(),
  startTime: z.string(),
  endTime: z.string().nullish(),
  estimatedDurationMinutes: z.number().int().nullish(),
  fieldId: z.string().nullable(),
  fieldLabel: z.string().nullable(),
  status: matchStatusSchema,
  home: matchTeamStateSchema,
  away: matchTeamStateSchema,
  capAt: z.number().int().nullish(),
  softCapMinutes: z.number().int().nullish(),
  hardCapMinutes: z.number().int().nullish(),
  updatedAt: z.string().nullish(),
});

// Full match schema with events and detailed info
export const matchSchema = matchSummarySchema.extend({
  stageId: z.string().nullish(),
  poolId: z.string().nullable(),
  venue: venueSchema.pick({ name: true, city: true, timezone: true }).nullish(),
  events: z.array(matchEventSchema),
  stats: z
    .object({
      breaksByTeam: z.record(z.string(), z.number().int()),
      completions: z.record(z.string(), z.number().int()).nullish(),
      turnovers: z.record(z.string(), z.number().int()).nullish(),
      pulls: z.record(z.string(), z.number().int()).nullish(),
    })
    .nullish(),
  broadcast: z
    .object({
      streamUrl: z.string().url().nullish(),
      commentators: z.array(personNameSchema).nullish(),
    })
    .nullish(),
  officials: z
    .array(
      z.object({
        name: personNameSchema,
        role: z.enum(["scorekeeper", "observer", "referee"]),
      }),
    )
    .nullish(),
});

export const standingEntrySchema = z.object({
  teamId: z.string(),
  rank: z.number().int(),
  wins: z.number().int(),
  losses: z.number().int(),
  pointsFor: z.number().int(),
  pointsAgainst: z.number().int(),
  pointDiff: z.number().int(),
  spiritAverage: z.number().min(0).max(5).nullable(),
  streak: z.string().nullable(),
});

const crossMatchRuleSchema = z
  .object({
    fromPool: z.string(),
    fromRank: z.number().int(),
    toPool: z.string().nullish(),
    toRank: z.number().int().nullish(),
  })
  .partial({ toPool: true, toRank: true });

const relegationRuleSchema = z
  .object({
    fromPool: z.string(),
    fromRank: z.number().int(),
    toStage: z.string().nullish(),
    toPool: z.string().nullish(),
  })
  .partial({ toStage: true, toPool: true });

const advancementRulesSchema = z
  .object({
    powerPoolSize: z.number().int().nullish(),
    crossMatches: z.array(crossMatchRuleSchema).nullish(),
    relegation: z.array(relegationRuleSchema).nullish(),
    slotsPerPool: z.number().int().nullish(),
    relegationPerPool: z.number().int().nullish(),
  })
  .partial()
  .passthrough();

const tournamentSettingsSchema = z
  .object({
    format: z.string(),
    poolCount: z.number().int().nullish(),
    teamsPerPool: z.number().int().nullish(),
    advancement: advancementRulesSchema.nullish(),
    restPeriods: z.number().int().nullish(),
    matchDurationMinutes: z.number().int().nullish(),
    fieldCount: z.number().int().nullish(),
    capAt: z.number().int().nullish(),
    softCapMinutes: z.number().int().nullish(),
    hardCapMinutes: z.number().int().nullish(),
  })
  .passthrough();

export const poolSchema = z.object({
  id: z.string(),
  label: z.string(),
  stageId: z.string(),
  teams: z.array(
    z.object({
      teamId: z.string(),
      seed: z.number().int(),
    }),
  ),
  standings: z.array(standingEntrySchema).nullish(),
});

export const stageSchema = z.object({
  id: z.string(),
  name: z.string(),
  stageType: stageTypeSchema,
  division: divisionSchema,
  pools: z.array(poolSchema),
  schedule: z.array(matchSchema.omit({ events: true })).nullish(),
});

export const spiritScoreSchema = z.object({
  teamId: z.string(),
  opponentTeamId: z.string(),
  matchId: z.string(),
  rubric: z.object({
    rulesKnowledge: z.number().min(0).max(4),
    fouls: z.number().min(0).max(4),
    fairness: z.number().min(0).max(4),
    positiveAttitude: z.number().min(0).max(4),
    communication: z.number().min(0).max(4),
  }),
  total: z.number().min(0).max(25),
  notes: z.string().nullable(),
});

export const tournamentSchema = z.object({
  id: z.string(),
  slug: z.string(),
  name: z.string(),
  season: z.string(),
  division: divisionSchema,
  startDate: z.string(),
  endDate: z.string(),
  status: tournamentStatusSchema,
  organiser: z
    .object({
      name: z.string(),
      website: z.string().url().nullish(),
      contactEmail: z.string().email().nullish(),
    })
    .optional(),
  venue: venueSchema,
  stages: z.array(stageSchema),
  teams: z.array(
    z.object({
      teamId: z.string(),
      seed: z.number().int(),
    }),
  ),
  settings: tournamentSettingsSchema.nullish(),
  standings: z.array(standingEntrySchema).nullish(),
  spiritStandings: z.array(
    z.object({
      teamId: z.string(),
      average: z.number().min(0).max(5),
    }),
  ).nullish(),
  updatedAt: z.string(),
});

export const seasonSummarySchema = z.object({
  id: z.string(),
  label: z.string(),
  year: z.number().int(),
  divisions: z.array(divisionSchema),
  tournaments: z.array(
    tournamentSchema.pick({
      id: true,
      slug: true,
      name: true,
      startDate: true,
      endDate: true,
      status: true,
      division: true,
    }),
  ),
});

export type Division = z.infer<typeof divisionSchema>;
export type TournamentStatus = z.infer<typeof tournamentStatusSchema>;
export type StageType = z.infer<typeof stageTypeSchema>;
export type MatchStatus = z.infer<typeof matchStatusSchema>;
export type TurnoverType = z.infer<typeof turnoverTypeSchema>;
export type TimeoutType = z.infer<typeof timeoutTypeSchema>;
export type Player = z.infer<typeof playerSchema>;
export type PlayerTeamHistory = z.infer<typeof playerTeamHistorySchema>;
export type Team = z.infer<typeof teamSchema>;
export type TeamSeasonSummary = z.infer<typeof teamSeasonSummarySchema>;
export type Venue = z.infer<typeof venueSchema>;
export type MatchEvent = z.infer<typeof matchEventSchema>;
export type Match = z.infer<typeof matchSchema>;
export type StandingEntry = z.infer<typeof standingEntrySchema>;
export type AdvancementRules = z.infer<typeof advancementRulesSchema>;
export type Pool = z.infer<typeof poolSchema>;
export type Stage = z.infer<typeof stageSchema>;
export type SpiritScore = z.infer<typeof spiritScoreSchema>;
export type Tournament = z.infer<typeof tournamentSchema>;
export type SeasonSummary = z.infer<typeof seasonSummarySchema>;
export type MatchSummary = z.infer<typeof matchSummarySchema>;
export type TournamentSettings = z.infer<typeof tournamentSettingsSchema>;

