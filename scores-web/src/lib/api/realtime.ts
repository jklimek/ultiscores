import { z } from "zod";

import {
  matchEventSchema,
  matchSchema,
  matchStatusSchema,
  spiritScoreSchema,
} from "@/lib/api/schemas";

export const liveMessageTypeSchema = z.enum([
  "connection_ack",
  "match_snapshot",
  "score_update",
  "event_created",
  "timeout_taken",
  "spirit_updated",
  "error",
]);

export const matchSnapshotSchema = z.object({
  type: z.literal("match_snapshot"),
  match: matchSchema,
});

export const scoreUpdateSchema = z.object({
  type: z.literal("score_update"),
  matchId: z.string(),
  homeScore: z.number().int(),
  awayScore: z.number().int(),
  status: matchStatusSchema,
  clockLabel: z.string().nullable(),
  updatedAt: z.string(),
});

export const eventCreatedSchema = z.object({
  type: z.literal("event_created"),
  matchId: z.string(),
  event: matchEventSchema,
});

export const timeoutTakenSchema = z.object({
  type: z.literal("timeout_taken"),
  matchId: z.string(),
  teamId: z.string(),
  remaining: z.number().int(),
  timeoutType: z.enum(["team", "official", "spirit"]),
});

export const spiritUpdatedSchema = z.object({
  type: z.literal("spirit_updated"),
  matchId: z.string(),
  teamId: z.string(),
  spirit: spiritScoreSchema,
});

export const liveErrorSchema = z.object({
  type: z.literal("error"),
  code: z.string(),
  message: z.string(),
  details: z.unknown().optional(),
});

export const liveConnectionAckSchema = z.object({
  type: z.literal("connection_ack"),
  matchId: z.string(),
  heartbeatInterval: z.number().int(),
});

export const liveMessageSchema = z.discriminatedUnion("type", [
  liveConnectionAckSchema,
  matchSnapshotSchema,
  scoreUpdateSchema,
  eventCreatedSchema,
  timeoutTakenSchema,
  spiritUpdatedSchema,
  liveErrorSchema,
]);

export type LiveMessage = z.infer<typeof liveMessageSchema>;
export type MatchSnapshotMessage = z.infer<typeof matchSnapshotSchema>;
export type ScoreUpdateMessage = z.infer<typeof scoreUpdateSchema>;
export type EventCreatedMessage = z.infer<typeof eventCreatedSchema>;
export type TimeoutTakenMessage = z.infer<typeof timeoutTakenSchema>;
export type SpiritUpdatedMessage = z.infer<typeof spiritUpdatedSchema>;
export type LiveErrorMessage = z.infer<typeof liveErrorSchema>;

