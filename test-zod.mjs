#!/usr/bin/env node
import { z } from 'zod';

// Reproduce the frontend schemas
const divisionSchema = z.enum(["open", "women", "mixed", "junior", "masters"]);
const tournamentStatusSchema = z.enum(["upcoming", "in_progress", "completed", "cancelled"]);
const stageTypeSchema = z.enum(["round_robin", "pool", "bracket", "placement", "relegation"]);

const venueSchema = z.object({
  name: z.string(),
  city: z.string(),
  country: z.string(),
  latitude: z.number().nullable(),
  longitude: z.number().nullable(),
  address: z.string().optional(),
  timezone: z.string(),
  fields: z.array(
    z.object({
      id: z.string(),
      label: z.string(),
      surface: z.enum(["grass", "turf", "indoor", "sand"]).optional(),
    })
  ),
});

const standingEntrySchema = z.object({
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

const poolSchema = z.object({
  id: z.string(),
  label: z.string(),
  stageId: z.string(),
  teams: z.array(
    z.object({
      teamId: z.string(),
      seed: z.number().int(),
    })
  ),
  standings: z.array(standingEntrySchema).optional(),
});

const stageSchema = z.object({
  id: z.string(),
  name: z.string(),
  stageType: stageTypeSchema,
  division: divisionSchema,
  pools: z.array(poolSchema),
  schedule: z.array(z.any()).optional(), // Simplified
});

const tournamentSchema = z.object({
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
      website: z.string().url().optional(),
      contactEmail: z.string().email().optional(),
    })
    .optional(),
  venue: venueSchema,
  stages: z.array(stageSchema),
  teams: z.array(
    z.object({
      teamId: z.string(),
      seed: z.number().int(),
    })
  ),
  standings: z.array(standingEntrySchema).optional(),
  spiritStandings: z.array(
    z.object({
      teamId: z.string(),
      average: z.number().min(0).max(5),
    })
  ).optional(),
  updatedAt: z.string(),
});

// Fetch and test
const response = await fetch('http://localhost:8000/v1/tournaments/');
const data = await response.json();

console.log('🔍 Testing Zod validation...\n');

for (let i = 0; i < data.length; i++) {
  const tournament = data[i];
  console.log(`Tournament ${i + 1}: ${tournament.name}`);
  
  const result = tournamentSchema.safeParse(tournament);
  
  if (!result.success) {
    console.log('❌ VALIDATION FAILED:');
    console.log(JSON.stringify(result.error.issues, null, 2));
  } else {
    console.log('✅ VALIDATION PASSED');
  }
  console.log('');
}

