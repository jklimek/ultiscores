import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getApiClient } from "@/lib/api/server";
import { createMockApiClient } from "@/lib/api/mock-client";
import { formatDivision } from "@/lib/format";

export default async function TeamsPage() {
  const api = getApiClient();
  let teams = [];
  
  try {
    teams = await api.listTeams();
  } catch (error) {
    console.error("Failed to fetch teams from API, using mocks:", error);
    const mockApi = createMockApiClient();
    teams = await mockApi.listTeams();
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
      <header className="space-y-4">
        <h1 className="text-4xl font-semibold tracking-tight">Teams</h1>
        <p className="max-w-3xl text-base text-muted-foreground">
          Discover clubs competing across Polish Ultimate divisions. View
          rosters, season history, and recent results with just a tap.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {teams.map((team) => (
          <Card
            key={team.id}
            className="border-border/70 bg-card/80 shadow-sm transition hover:shadow-lg"
          >
            <CardHeader className="space-y-3">
              <div className="flex items-center justify-between">
                <Badge variant="outline" className="capitalize">
                  {formatDivision(team.division)}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  Founded {team.foundedYear ?? "—"}
                </span>
              </div>
              <CardTitle className="text-xl font-semibold">
                <Link href={`/teams/${team.slug}`}>{team.name}</Link>
              </CardTitle>
              <CardDescription>
                {team.city ?? "Unknown city"}, {team.country ?? "PL"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p>
                Latest season:{" "}
                {team.seasons.at(-1)?.season ?? "Season details coming soon"}
              </p>
              <p>
                Tournament finishes:{" "}
                {team.seasons
                  .flatMap((season) => season.tournaments)
                  .slice(-3)
                  .map((tournament) => `${tournament.placement ?? "—"} place`)
                  .join(", ") || "Awaiting results"}
              </p>
              <Link
                href={`/teams/${team.slug}`}
                className="inline-flex text-sm font-medium text-primary underline-offset-4 hover:underline"
              >
                View team →
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

