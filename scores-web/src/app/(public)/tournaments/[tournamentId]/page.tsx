import Link from "next/link";
import { notFound } from "next/navigation";
import clsx from "clsx";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getApiClient } from "@/lib/api/server";
import { createMockApiClient } from "@/lib/api/mock-client";
import {
  formatDate,
  formatDateRange,
  formatDateTime,
  formatDivision,
} from "@/lib/format";
import type {
  AdvancementRules,
  MatchSummary,
  Pool,
  SpiritScore,
  Stage,
  Team,
  Tournament,
} from "@/lib/api/schemas";

type TournamentPageProps = {
  params: Promise<{
    tournamentId: string;
  }>;
};

type PoolRow = {
  teamId: string;
  rank: number;
  wins: number | null;
  losses: number | null;
  pointDiff: number | null;
  seed: number | null;
};

type AdvancementProjection = {
  advance: number;
  relegate: number;
};

const PLAYOFF_ROUND_ORDER = [
  "grand final",
  "final",
  "finals",
  "bronze",
  "third place",
  "semifinal",
  "semifinals",
  "quarterfinal",
  "quarterfinals",
  "round of 16",
];

export default async function TournamentPage({ params }: TournamentPageProps) {
  const { tournamentId } = await params;
  const api = getApiClient();

  let tournament: Tournament | undefined;
  try {
    tournament = await api.getTournament(tournamentId);
  } catch (error) {
    console.error("Failed to fetch tournament from API, trying mocks:", error);
    try {
      const mockApi = createMockApiClient();
      tournament = await mockApi.getTournament(tournamentId);
    } catch (mockError) {
      console.error("Unable to load tournament from mocks:", mockError);
      notFound();
    }
  }

  if (!tournament) {
    notFound();
  }

  let matches: MatchSummary[] = [];
  let spiritScores: SpiritScore[] = [];
  let teams: Team[] = [];

  try {
    [matches, spiritScores, teams] = await Promise.all([
      api.listMatches({ tournamentId: tournament.id }),
      api.listSpiritScores(tournament.id),
      api.listTeams(),
    ]);
  } catch (error) {
    console.warn("Falling back to mock data for tournament details:", error);
    const mockApi = createMockApiClient();
    [matches, spiritScores, teams] = await Promise.all([
      mockApi.listMatches({ tournamentId: tournament.id }),
      mockApi.listSpiritScores(tournament.id),
      mockApi.listTeams(),
    ]);
  }

  const teamMap = new Map<string, Team>(teams.map((team) => [team.id, team]));

  const resolveTeam = (teamId: string) => {
    const team = teamMap.get(teamId);
    return {
      slug: team?.slug ?? teamId,
      name: team?.name ?? teamId,
      shortName: team?.shortName ?? team?.name ?? teamId,
      city: team?.city ?? undefined,
    };
  };

  const liveMatches = matches.filter((match) => match.status === "live");
  const playoffRounds = groupPlayoffMatches(matches);
  const poolStages = tournament.stages.filter((stage) => stage.pools.length > 0);
  const totalPools = poolStages.reduce(
    (acc, stage) => acc + stage.pools.length,
    0,
  );
  const poolDisplayCount =
    tournament.settings?.poolCount ??
    (totalPools > 0 ? totalPools : undefined);

  const structuredPoolStages = poolStages.map((stage) => ({
    stage,
    pools: stage.pools.map((pool) => {
      const rows = buildPoolRows(pool);
      const projection = deriveAdvancement(stage, pool, tournament);
      return { pool, rows, projection };
    }),
  }));

  const advancementSummary = structuredPoolStages.flatMap(({ stage, pools }) =>
    pools.map(({ pool, rows, projection }) => ({
      stageName: stage.name,
      poolLabel: pool.label,
      advancingTeams: rows
        .slice(0, projection.advance)
        .map((row) => resolveTeam(row.teamId).name),
      relegatedTeams:
        projection.relegate > 0
          ? rows
              .slice(rows.length - projection.relegate)
              .map((row) => resolveTeam(row.teamId).name)
          : [],
    })),
  );

  const tournamentTeams = tournament.teams
    .map((seedEntry) => {
      const team = teamMap.get(seedEntry.teamId);
      const rosterForTournament =
        team?.roster.filter((entry) => entry.tournamentId === tournament.id) ??
        [];
      const keyPlayers =
        (rosterForTournament.length > 0
          ? rosterForTournament
          : team?.roster ?? []
        ).slice(0, 4);
      return {
        seed: seedEntry.seed,
        teamId: seedEntry.teamId,
        team,
        keyPlayers,
      };
    })
    .sort((a, b) => a.seed - b.seed);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
      <header className="space-y-6 rounded-3xl border border-border/60 bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="capitalize">
                {formatDivision(tournament.division)}
              </Badge>
              <Badge variant="outline" className="capitalize">
                {tournament.status.replace("_", " ")}
              </Badge>
            </div>
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              {tournament.name}
            </h1>
            <p className="text-sm text-muted-foreground">
              {formatDateRange(tournament.startDate, tournament.endDate)} •{" "}
              {tournament.venue.city}, {tournament.venue.country}
            </p>
          </div>
          <div className="text-right text-sm text-muted-foreground">
            <p>
              Venue: <strong>{tournament.venue.name}</strong>
            </p>
            <p>Organiser: {tournament.organiser?.name ?? "TBA"}</p>
            <p>Updated {formatDateTime(tournament.updatedAt)}</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="text-sm text-muted-foreground">Teams</p>
            <p className="mt-2 text-2xl font-semibold">
              {tournament.teams.length}
            </p>
            <p className="text-xs text-muted-foreground">
              Seeded draw with roster access below
            </p>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="text-sm text-muted-foreground">Fields</p>
            <p className="mt-2 text-2xl font-semibold">
              {tournament.venue.fields.length}
            </p>
            <p className="text-xs text-muted-foreground">
              {tournament.venue.fields.map((field) => field.label).join(", ")}
            </p>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="text-sm text-muted-foreground">Format</p>
            <p className="mt-2 text-2xl font-semibold capitalize">
              {tournament.settings?.format ?? "custom"}
            </p>
            <p className="text-xs text-muted-foreground">
              Pools: {poolDisplayCount ?? "—"}
            </p>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="text-sm text-muted-foreground">Stages</p>
            <p className="mt-2 text-2xl font-semibold">
              {tournament.stages.length}
            </p>
            <p className="text-xs text-muted-foreground">
              {tournament.stages.map((stage) => stage.name).join(" → ")}
            </p>
          </div>
        </div>
      </header>

      <Tabs defaultValue="overview">
        <TabsList className="flex flex-wrap">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="structure">Structure</TabsTrigger>
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
          <TabsTrigger value="standings">Standings</TabsTrigger>
          <TabsTrigger value="spirit">Spirit</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-8 space-y-6">
          {liveMatches.length > 0 ? (
            <section className="space-y-4">
              <h2 className="text-2xl font-semibold">Live now</h2>
              <div className="grid gap-4 md:grid-cols-2">
                {liveMatches.map((match) => {
                  const home = resolveTeam(match.home.teamId);
                  const away = resolveTeam(match.away.teamId);
                  return (
                    <Card key={match.id} className="border-border/70">
                      <CardHeader>
                        <CardTitle className="text-lg">
                          <Link
                            href={`/teams/${home.slug}`}
                            className="text-primary underline-offset-4 hover:underline"
                          >
                            {home.name}
                          </Link>{" "}
                          vs{" "}
                          <Link
                            href={`/teams/${away.slug}`}
                            className="text-primary underline-offset-4 hover:underline"
                          >
                            {away.name}
                          </Link>
                        </CardTitle>
                        <CardDescription>
                          Field {match.fieldLabel ?? match.fieldId ?? "TBC"} •{" "}
                          {formatDate(match.startTime)}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="flex items-center justify-between">
                        <div className="flex flex-col items-center">
                          <span className="text-lg font-semibold">
                            {match.home.score}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {home.shortName}
                          </span>
                        </div>
                        <div className="text-xs uppercase tracking-wide text-muted-foreground">
                          {match.status}
                        </div>
                        <div className="flex flex-col items-center">
                          <span className="text-lg font-semibold">
                            {match.away.score}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {away.shortName}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </section>
          ) : null}

          {playoffRounds.length > 0 ? (
            <section className="space-y-4">
              <h2 className="text-2xl font-semibold">Playoffs snapshot</h2>
              <div className="grid gap-4 md:grid-cols-2">
                {playoffRounds.map(({ round, matches: roundMatches }) => (
                  <Card
                    key={round}
                    className="border-border/70 bg-card/80 backdrop-blur-sm"
                  >
                    <CardHeader>
                      <CardTitle className="text-lg">{round}</CardTitle>
                      <CardDescription>
                        {roundMatches.length}{" "}
                        {roundMatches.length === 1 ? "match" : "matches"}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {roundMatches.map((match) => {
                        const home = resolveTeam(match.home.teamId);
                        const away = resolveTeam(match.away.teamId);
                        return (
                          <div
                            key={match.id}
                            className="space-y-2 rounded-2xl border border-border/70 bg-background/80 p-4"
                          >
                            <div className="text-xs uppercase text-muted-foreground">
                              {formatDate(match.startTime)} •{" "}
                              {match.fieldLabel ?? match.fieldId ?? "TBC"}
                            </div>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2 text-sm">
                                <Link
                                  href={`/teams/${home.slug}`}
                                  className="font-medium text-primary underline-offset-4 hover:underline"
                                >
                                  {home.name}
                                </Link>
                                <span className="font-semibold">
                                  {match.home.score}
                                </span>
                              </div>
                              <span className="text-muted-foreground">vs</span>
                              <div className="flex items-center gap-2 text-sm">
                                <Link
                                  href={`/teams/${away.slug}`}
                                  className="font-medium text-primary underline-offset-4 hover:underline"
                                >
                                  {away.name}
                                </Link>
                                <span className="font-semibold">
                                  {match.away.score}
                                </span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          ) : null}

          <section className="grid gap-6 lg:grid-cols-2">
            <Card className="border-border/70">
              <CardHeader>
                <CardTitle className="text-xl">Venue details</CardTitle>
                <CardDescription>
                  Timezone: {tournament.venue.timezone}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-muted-foreground">
                <p>{tournament.venue.address}</p>
                <p>
                  Fields:{" "}
                  {tournament.venue.fields
                    .map((field) => field.label)
                    .join(", ")}
                </p>
                <p>
                  Coordinates: {tournament.venue.latitude},{" "}
                  {tournament.venue.longitude}
                </p>
              </CardContent>
              <CardFooter>
                <Link
                  href={`https://maps.google.com/?q=${encodeURIComponent(
                    `${tournament.venue.name} ${tournament.venue.city}`,
                  )}`}
                  target="_blank"
                  className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                >
                  Open in Maps →
                </Link>
              </CardFooter>
            </Card>
            <Card className="border-border/70">
              <CardHeader>
                <CardTitle className="text-xl">Organiser</CardTitle>
                <CardDescription>
                  Contacts for scorekeepers and volunteers.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <p>{tournament.organiser?.name ?? "To be announced."}</p>
                {tournament.organiser?.website ? (
                  <p>
                    Website:{" "}
                    <Link
                      href={tournament.organiser.website}
                      target="_blank"
                      className="text-primary underline-offset-4 hover:underline"
                    >
                      {tournament.organiser.website}
                    </Link>
                  </p>
                ) : null}
                {tournament.organiser?.contactEmail ? (
                  <p>Email: {tournament.organiser.contactEmail}</p>
                ) : null}
              </CardContent>
            </Card>
          </section>
        </TabsContent>

        <TabsContent
          value="structure"
          id="structure"
          className="mt-8 space-y-8"
        >
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold">Tournament structure</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {tournament.stages.map((stage, index) => {
                const stageProjection = structuredPoolStages.find(
                  (structured) => structured.stage.id === stage.id,
                );
                return (
                  <Card key={stage.id} className="border-border/70">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between text-lg">
                        <span>{stage.name}</span>
                        <Badge variant="outline" className="capitalize">
                          {stage.stageType.replace("_", " ")}
                        </Badge>
                      </CardTitle>
                      <CardDescription>
                        Stage {index + 1} •{" "}
                        {stage.pools.length}{" "}
                        {stage.pools.length === 1 ? "pool" : "pools"}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm text-muted-foreground">
                      <p>
                        Pools:{" "}
                        {stage.pools.length > 0
                          ? stage.pools.map((pool) => pool.label).join(", ")
                          : "Match-play"}
                      </p>
                      {stage.stageType === "pool" && stageProjection ? (
                        <p>
                          Top{" "}
                          {stageProjection.pools[0]?.projection.advance ?? "—"}{" "}
                          projected to advance.
                        </p>
                      ) : null}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </section>

          <section className="space-y-4" id="pools">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-semibold">
                  Pools & advancement simulation
                </h2>
                <p className="text-sm text-muted-foreground">
                  Highlighted teams are projected to move on based on current
                  standings (or seed order when games haven&apos;t been played).
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                <span className="flex items-center gap-2">
                  <span className="inline-flex h-3 w-3 rounded-full bg-emerald-500/70" />
                  Projected to advance
                </span>
                <span className="flex items-center gap-2">
                  <span className="inline-flex h-3 w-3 rounded-full bg-rose-500/70" />
                  At risk of relegation
                </span>
              </div>
            </div>

            {structuredPoolStages.length > 0 ? (
              structuredPoolStages.map(({ stage, pools }) => (
                <div key={stage.id} className="space-y-4">
                  <h3 className="text-xl font-semibold">{stage.name}</h3>
                  <div className="grid gap-4 lg:grid-cols-2">
                    {pools.map(({ pool, rows, projection }) => (
                      <Card
                        key={pool.id}
                        className="border-border/70 bg-card/80 backdrop-blur-sm"
                      >
                        <CardHeader>
                          <div className="flex items-center justify-between gap-4">
                            <CardTitle className="text-lg">{pool.label}</CardTitle>
                            <div className="text-xs text-muted-foreground">
                              Advance {projection.advance} •{" "}
                              {projection.relegate > 0
                                ? `Relegate ${projection.relegate}`
                                : "No relegation"}
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="overflow-hidden rounded-2xl border border-border/60">
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>#</TableHead>
                                  <TableHead>Team</TableHead>
                                  <TableHead>Record</TableHead>
                                  <TableHead>Diff</TableHead>
                                  <TableHead>Seed</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {rows.map((row, index) => {
                                  const teamInfo = resolveTeam(row.teamId);
                                  const isAdvancing = index < projection.advance;
                                  const isRelegated =
                                    projection.relegate > 0 &&
                                    index >= rows.length - projection.relegate;
                                  return (
                                    <TableRow
                                      key={row.teamId}
                                      className={clsx(
                                        "transition",
                                        isAdvancing &&
                                          "bg-emerald-500/10 backdrop-blur-sm",
                                        isRelegated &&
                                          "bg-rose-500/10 backdrop-blur-sm",
                                      )}
                                    >
                                      <TableCell className="font-medium">
                                        {row.rank}
                                      </TableCell>
                                      <TableCell>
                                        <Link
                                          href={`/teams/${teamInfo.slug}`}
                                          className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                                        >
                                          {teamInfo.name}
                                        </Link>
                                      </TableCell>
                                      <TableCell>
                                        {formatRecord(row.wins, row.losses)}
                                      </TableCell>
                                      <TableCell>
                                        {formatPointDiff(row.pointDiff)}
                                      </TableCell>
                                      <TableCell>{row.seed ?? "—"}</TableCell>
                                    </TableRow>
                                  );
                                })}
                              </TableBody>
                            </Table>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <Card className="border-dashed bg-background/60 text-muted-foreground">
                <CardContent className="py-12 text-center text-sm">
                  Pools will appear once the tournament generator publishes the
                  draw.
                </CardContent>
              </Card>
            )}
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold">Projected advancement</h2>
            {advancementSummary.length > 0 ? (
              <Card className="border-border/70">
                <CardContent className="space-y-3 py-6 text-sm">
                  {advancementSummary.map((item) => (
                    <div
                      key={`${item.stageName}-${item.poolLabel}`}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-border/60 bg-background/70 px-4 py-3"
                    >
                      <div>
                        <span className="font-medium">
                          {item.stageName} • {item.poolLabel}
                        </span>
                        <div className="text-xs text-muted-foreground">
                          {item.advancingTeams.length > 0
                            ? `Advancing: ${item.advancingTeams.join(", ")}`
                            : "Awaiting games to project advancement."}
                        </div>
                      </div>
                      {item.relegatedTeams.length > 0 ? (
                        <div className="text-xs text-rose-500">
                          Relegation: {item.relegatedTeams.join(", ")}
                        </div>
                      ) : null}
                    </div>
                  ))}
                </CardContent>
              </Card>
            ) : (
              <Card className="border-dashed bg-background/60 text-muted-foreground">
                <CardContent className="py-12 text-center text-sm">
                  We&apos;ll run projections once pool standings are available.
                </CardContent>
              </Card>
            )}
          </section>

          <section className="space-y-4" id="teams">
            <h2 className="text-2xl font-semibold">Teams & key players</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {tournamentTeams.map(({ seed, teamId, team, keyPlayers }) => (
                <Card key={teamId} className="border-border/70 bg-card/80">
                  <CardHeader className="space-y-3">
                    <div className="flex items-center justify-between gap-4">
                      <Badge variant="outline">Seed #{seed}</Badge>
                      {team?.city ? (
                        <span className="text-xs text-muted-foreground">
                          {team.city}, {team.country ?? "PL"}
                        </span>
                      ) : null}
                    </div>
                    <CardTitle className="text-xl font-semibold">
                      <Link
                        href={`/teams/${team?.slug ?? teamId}`}
                        className="text-primary underline-offset-4 hover:underline"
                      >
                        {team?.name ?? teamId}
                      </Link>
                    </CardTitle>
                    <CardDescription>
                      {keyPlayers.length > 0
                        ? `Highlighting ${keyPlayers.length} recent players`
                        : "Add players in the admin app to surface rosters here."}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    {keyPlayers.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {keyPlayers.map((entry) => (
                          <Link
                            key={entry.player.id}
                            href={`/players/${entry.player.id}`}
                            className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground hover:bg-secondary/80 hover:underline"
                          >
                            {entry.player.name.display}
                          </Link>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-muted-foreground">
                        Tournament roster will appear once submitted.
                      </p>
                    )}
                  </CardContent>
                  <CardFooter className="flex items-center justify-between text-xs text-muted-foreground">
                    <Link
                      href="#schedule"
                      className="font-medium text-primary underline-offset-4 hover:underline"
                    >
                      Upcoming matches
                    </Link>
                    <Link
                      href={`/teams/${team?.slug ?? teamId}`}
                      className="font-medium text-primary underline-offset-4 hover:underline"
                    >
                      View team →
                    </Link>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </section>
        </TabsContent>

        <TabsContent
          value="schedule"
          id="schedule"
          className="mt-8 space-y-6"
        >
          <h2 className="text-2xl font-semibold">Full schedule</h2>
          <ScrollArea className="h-[540px] rounded-3xl border border-border/70">
            <div className="divide-y divide-border/70">
              {matches.map((match) => {
                const home = resolveTeam(match.home.teamId);
                const away = resolveTeam(match.away.teamId);
                return (
                  <div
                    key={match.id}
                    className="grid gap-4 p-4 sm:grid-cols-[1fr_auto]"
                  >
                    <div className="space-y-2">
                      <p className="text-sm font-medium uppercase text-muted-foreground">
                        {match.round} • {formatDate(match.startTime)} • Field{" "}
                        {match.fieldLabel ?? match.fieldId ?? "TBC"}
                      </p>
                      <div className="flex items-center justify-between gap-4 rounded-2xl border border-border/70 bg-background/80 px-4 py-3">
                        <div className="flex flex-col gap-1 text-sm">
                          <Link
                            href={`/teams/${home.slug}`}
                            className="font-medium text-primary underline-offset-4 hover:underline"
                          >
                            {home.name}
                          </Link>
                          <span className="text-xs text-muted-foreground">
                            Spirit {match.home.spiritScore ?? "—"}
                          </span>
                        </div>
                        <span className="text-lg font-semibold">
                          {match.home.score}
                        </span>
                      </div>
                      <div className="flex items-center justify-between gap-4 rounded-2xl border border-border/70 bg-background/80 px-4 py-3">
                        <div className="flex flex-col gap-1 text-sm">
                          <Link
                            href={`/teams/${away.slug}`}
                            className="font-medium text-primary underline-offset-4 hover:underline"
                          >
                            {away.name}
                          </Link>
                          <span className="text-xs text-muted-foreground">
                            Spirit {match.away.spiritScore ?? "—"}
                          </span>
                        </div>
                        <span className="text-lg font-semibold">
                          {match.away.score}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-start justify-end text-right text-xs text-muted-foreground">
                      <div className="space-y-1">
                        <p>Status: {match.status}</p>
                        {match.capAt ? <p>Point cap: {match.capAt}</p> : null}
                        {match.softCapMinutes ? (
                          <p>Soft cap: {match.softCapMinutes}′</p>
                        ) : null}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent
          value="standings"
          id="standings"
          className="mt-8 space-y-6"
        >
          <h2 className="text-2xl font-semibold">Standings</h2>
          {tournament.standings ? (
            <div className="overflow-hidden rounded-3xl border border-border/70">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rank</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead>W</TableHead>
                    <TableHead>L</TableHead>
                    <TableHead>PF</TableHead>
                    <TableHead>PA</TableHead>
                    <TableHead>Diff</TableHead>
                    <TableHead>Spirit</TableHead>
                    <TableHead>Streak</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tournament.standings.map((entry) => {
                    const team = resolveTeam(entry.teamId);
                    return (
                      <TableRow key={entry.teamId}>
                        <TableCell>{entry.rank}</TableCell>
                        <TableCell>
                          <Link
                            href={`/teams/${team.slug}`}
                            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                          >
                            {team.name}
                          </Link>
                        </TableCell>
                        <TableCell>{entry.wins}</TableCell>
                        <TableCell>{entry.losses}</TableCell>
                        <TableCell>{entry.pointsFor}</TableCell>
                        <TableCell>{entry.pointsAgainst}</TableCell>
                        <TableCell>{entry.pointDiff}</TableCell>
                        <TableCell>
                          {entry.spiritAverage
                            ? entry.spiritAverage.toFixed(2)
                            : "—"}
                        </TableCell>
                        <TableCell>{entry.streak ?? "—"}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          ) : (
            <Card className="border-dashed bg-background/60 text-muted-foreground">
              <CardContent className="py-12 text-center text-sm">
                Standings will appear once pool play is underway.
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="spirit" id="spirit" className="mt-8 space-y-6">
          <h2 className="text-2xl font-semibold">Spirit of the Game</h2>
          {spiritScores.length > 0 ? (
            <div className="overflow-hidden rounded-3xl border border-border/70">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Team</TableHead>
                    <TableHead>Opponent</TableHead>
                    <TableHead>Total</TableHead>
                    <TableHead>Notes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {spiritScores.map((score) => {
                    const team = resolveTeam(score.teamId);
                    const opponent = resolveTeam(score.opponentTeamId);
                    return (
                      <TableRow key={`${score.teamId}-${score.matchId}`}>
                        <TableCell>
                          <Link
                            href={`/teams/${team.slug}`}
                            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                          >
                            {team.name}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <Link
                            href={`/teams/${opponent.slug}`}
                            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                          >
                            {opponent.name}
                          </Link>
                        </TableCell>
                        <TableCell>{score.total}</TableCell>
                        <TableCell>{score.notes ?? "—"}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          ) : (
            <Card className="border-dashed bg-background/60 text-muted-foreground">
              <CardContent className="py-12 text-center text-sm">
                Spirit submissions will appear here after each round.
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

function buildPoolRows(pool: Pool): PoolRow[] {
  if (pool.standings && pool.standings.length > 0) {
    return pool.standings
      .slice()
      .sort((a, b) => a.rank - b.rank)
      .map((entry) => {
        const matchingSeed = pool.teams.find(
          (team) => team.teamId === entry.teamId,
        );
        return {
          teamId: entry.teamId,
          rank: entry.rank,
          wins: entry.wins,
          losses: entry.losses,
          pointDiff: entry.pointDiff,
          seed: matchingSeed?.seed ?? null,
        };
      });
  }

  return pool.teams
    .slice()
    .sort((a, b) => a.seed - b.seed)
    .map((team, index) => ({
      teamId: team.teamId,
      rank: index + 1,
      wins: null,
      losses: null,
      pointDiff: null,
      seed: team.seed ?? null,
    }));
}

function deriveAdvancement(
  stage: Stage,
  pool: Pool,
  tournament: Tournament,
): AdvancementProjection {
  const settings = tournament.settings;
  const advancement = (settings?.advancement ?? undefined) as
    | AdvancementRules
    | undefined;

  const poolCount =
    stage.pools.length ||
    settings?.poolCount ||
    Math.max(1, tournament.stages.length);

  let advance = 0;
  if (
    advancement &&
    typeof advancement.slotsPerPool === "number" &&
    advancement.slotsPerPool > 0
  ) {
    advance = advancement.slotsPerPool;
  } else if (
    advancement?.powerPoolSize &&
    typeof advancement.powerPoolSize === "number"
  ) {
    advance = Math.max(
      1,
      Math.round(advancement.powerPoolSize / Math.max(poolCount, 1)),
    );
  } else if (settings?.teamsPerPool && settings.teamsPerPool > 0) {
    advance = Math.max(1, Math.ceil(settings.teamsPerPool / 2));
  } else {
    advance = Math.max(1, Math.ceil(pool.teams.length / 2));
  }
  advance = Math.min(advance, pool.teams.length);

  let relegate = 0;
  if (
    advancement &&
    typeof advancement.relegationPerPool === "number" &&
    advancement.relegationPerPool > 0
  ) {
    relegate = Math.min(
      advancement.relegationPerPool,
      Math.max(0, pool.teams.length - advance),
    );
  } else if (Array.isArray(advancement?.relegation)) {
    relegate = advancement.relegation.filter((rule) => {
      if (!rule || typeof rule !== "object") {
        return false;
      }
      const recordRule = rule as Record<string, unknown>;
      const fromPool =
        typeof recordRule.fromPool === "string"
          ? (recordRule.fromPool as string)
          : typeof recordRule.toPool === "string"
            ? (recordRule.toPool as string)
            : undefined;
      return (
        !fromPool ||
        fromPool === pool.id ||
        fromPool === pool.label ||
        fromPool === stage.id
      );
    }).length;
    relegate = Math.min(relegate, Math.max(0, pool.teams.length - advance));
  }

  return {
    advance,
    relegate: Math.max(0, relegate),
  };
}

function groupPlayoffMatches(matches: MatchSummary[]) {
  const playoffKeywords = ["final", "semi", "quarter", "bronze", "third"];
  const grouped = new Map<string, MatchSummary[]>();

  matches.forEach((match) => {
    const roundLower = match.round.toLowerCase();
    if (playoffKeywords.some((keyword) => roundLower.includes(keyword))) {
      const existing = grouped.get(match.round) ?? [];
      existing.push(match);
      grouped.set(match.round, existing);
    }
  });

  return Array.from(grouped.entries())
    .sort((a, b) => getPlayoffRoundIndex(a[0]) - getPlayoffRoundIndex(b[0]))
    .map(([round, roundMatches]) => ({
      round,
      matches: roundMatches,
    }));
}

function getPlayoffRoundIndex(round: string) {
  const index = PLAYOFF_ROUND_ORDER.findIndex((label) =>
    round.toLowerCase().includes(label),
  );
  return index === -1 ? PLAYOFF_ROUND_ORDER.length : index;
}

function formatRecord(wins: number | null, losses: number | null) {
  if (wins === null || losses === null) {
    return "—";
  }
  return `${wins}-${losses}`;
}

function formatPointDiff(pointDiff: number | null) {
  if (pointDiff === null) {
    return "—";
  }
  return pointDiff > 0 ? `+${pointDiff}` : `${pointDiff}`;
}

export async function generateStaticParams() {
  const api = getApiClient();
  try {
    const tournaments = await api.listTournaments();
    return tournaments.map((t) => ({
      tournamentId: t.slug ?? t.id,
    }));
  } catch (error) {
    console.warn(
      "Falling back to mock tournaments for static params generation:",
      error,
    );
    const mockApi = createMockApiClient();
    const tournaments = await mockApi.listTournaments();
    return tournaments.map((t) => ({
      tournamentId: t.slug ?? t.id,
    }));
  }
}

