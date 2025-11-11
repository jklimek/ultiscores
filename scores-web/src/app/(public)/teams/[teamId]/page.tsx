import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import { formatDate, formatDivision } from "@/lib/format";

type TeamPageProps = {
  params: Promise<{
    teamId: string;
  }>;
};

export default async function TeamPage({ params }: TeamPageProps) {
  const { teamId } = await params;
  const api = getApiClient();

  let team;
  try {
    team = await api.getTeam(teamId);
  } catch {
    notFound();
  }

  let matches = [];
  try {
    matches = await api.listMatches({ teamId: team.id });
  } catch (error) {
    console.error("Failed to fetch matches from API, using mocks:", error);
    const mockApi = createMockApiClient();
    matches = await mockApi.listMatches({ teamId: team.id });
  }
  const latestSeason = team.seasons.at(-1);
  const latestTournamentId = team.roster.at(-1)?.tournamentId;
  const latestRoster = latestTournamentId
    ? team.roster.filter((entry) => entry.tournamentId === latestTournamentId)
    : team.roster;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
      <header className="space-y-6 rounded-3xl border border-border/60 bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <Badge variant="secondary" className="capitalize">
              {formatDivision(team.division)}
            </Badge>
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              {team.name}
            </h1>
            <p className="text-sm text-muted-foreground">
              {team.city ?? "Unknown city"}, {team.country ?? "PL"}
            </p>
          </div>
          <div className="text-right text-sm text-muted-foreground">
            <p>Short name: {team.shortName}</p>
            <p>Club: {team.clubName ?? "—"}</p>
            <p>Founded: {team.foundedYear ?? "—"}</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="text-sm text-muted-foreground">Latest season</p>
            <p className="mt-2 text-2xl font-semibold">
              {latestSeason?.season ?? "—"}
            </p>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="text-sm text-muted-foreground">Tournaments played</p>
            <p className="mt-2 text-2xl font-semibold">
              {latestSeason?.tournaments.length ?? 0}
            </p>
          </div>
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="text-sm text-muted-foreground">Last placement</p>
            <p className="mt-2 text-2xl font-semibold">
              {latestSeason?.tournaments.at(-1)?.placement ?? "—"}
            </p>
          </div>
        </div>
      </header>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="roster">Roster</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-8 space-y-6">
          <Card className="border-border/70">
            <CardHeader>
              <CardTitle className="text-xl">Recent matches</CardTitle>
              <CardDescription>
                Results from the latest competitions.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {matches.length > 0 ? (
                matches.slice(0, 5).map((match) => (
                  <div
                    key={match.id}
                    className="flex flex-col gap-3 rounded-2xl border border-border/70 bg-background/70 p-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        {formatDate(match.startTime)} • {match.round}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Field {match.fieldLabel ?? match.fieldId ?? "TBC"}
                      </p>
                    </div>
                    <div className="flex items-center gap-6 text-sm font-semibold">
                      <span>
                        {match.home.teamId === team.id
                          ? team.shortName
                          : match.home.teamId}
                        {"  "}
                        {match.home.score}
                      </span>
                      <span className="text-muted-foreground">vs</span>
                      <span>
                        {match.away.teamId === team.id
                          ? team.shortName
                          : match.away.teamId}
                        {"  "}
                        {match.away.score}
                      </span>
                    </div>
                    <span className="text-xs uppercase tracking-wide text-muted-foreground">
                      {match.status}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">
                  Match results will appear when the season begins.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roster" className="mt-8 space-y-6">
          <Card className="border-border/70">
            <CardHeader>
              <CardTitle className="text-xl">Tournament roster</CardTitle>
              <CardDescription>
                {latestTournamentId
                  ? `Most recent roster from tournament ${latestTournamentId}.`
                  : "Latest roster entries per tournament."}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-hidden rounded-3xl border border-border/60">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>#</TableHead>
                      <TableHead>Player</TableHead>
                      <TableHead>Roles</TableHead>
                      <TableHead>Captain</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {latestRoster.map((entry) => (
                      <TableRow key={entry.player.id}>
                        <TableCell>{entry.jerseyNumber ?? "—"}</TableCell>
                        <TableCell>
                          <Link
                            href={`/players/${entry.player.id}`}
                            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                          >
                            {entry.player.name.display}
                          </Link>
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {entry.player.roles.join(", ") || "—"}
                        </TableCell>
                        <TableCell>{entry.captain ? "Yes" : "No"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="mt-8 space-y-6">
          <Card className="border-border/70">
            <CardHeader>
              <CardTitle className="text-xl">Tournament history</CardTitle>
              <CardDescription>
                Placements from past tournaments across divisions.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {team.seasons.map((season) => (
                <div key={season.season} className="space-y-2">
                  <p className="font-medium">
                    {season.season} • {formatDivision(season.division)}
                  </p>
                  <ul className="space-y-1 text-muted-foreground">
                    {season.tournaments.map((tournament) => (
                      <li key={tournament.tournamentId}>
                        <Link
                          href={`/tournaments/${tournament.tournamentId}`}
                          className="text-primary underline-offset-4 hover:underline"
                        >
                          {tournament.tournamentName}
                        </Link>{" "}
                        —{" "}
                        {typeof tournament.placement === "number"
                          ? `${tournament.placement}. place`
                          : "Placement TBC"}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

