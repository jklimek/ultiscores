import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getApiClient } from "@/lib/api/server";
import { createMockApiClient } from "@/lib/api/mock-client";
import { formatDateRange, formatDivision } from "@/lib/format";

function partitionByStatus<T extends { status: string }>(items: T[]) {
  return items.reduce(
    (acc, item) => {
      acc[item.status as keyof typeof acc].push(item);
      return acc;
    },
    {
      upcoming: [] as T[],
      in_progress: [] as T[],
      completed: [] as T[],
      cancelled: [] as T[],
    },
  );
}

export default async function TournamentsPage() {
  const api = getApiClient();
  let tournaments = [];
  
  try {
    tournaments = await api.listTournaments();
  } catch (error) {
    console.error("Failed to fetch tournaments from API, using mocks:", error);
    const mockApi = createMockApiClient();
    tournaments = await mockApi.listTournaments();
  }
  
  const grouped = partitionByStatus(tournaments);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
      <header className="space-y-4">
        <h1 className="text-4xl font-semibold tracking-tight">
          Tournaments
        </h1>
        <p className="max-w-3xl text-base text-muted-foreground">
          Browse community leagues, beach festivals, and national championships.
          Every bracket and spirit score is collected so players, friends, and
          family can follow along without hunting through spreadsheets.
        </p>
      </header>

      <Tabs defaultValue="in_progress" className="w-full">
        <TabsList>
          <TabsTrigger value="in_progress">In progress</TabsTrigger>
          <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="cancelled">Cancelled</TabsTrigger>
        </TabsList>

        {(
          [
            ["in_progress", "Live events"],
            ["upcoming", "Mark your calendar"],
            ["completed", "Final results"],
            ["cancelled", "Archive"],
          ] as const
        ).map(([status, label]) => (
          <TabsContent key={status} value={status} className="mt-8 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold">{label}</h2>
              <span className="text-sm text-muted-foreground">
                {grouped[status].length} tournaments
              </span>
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              {grouped[status].map((tournament) => (
                <Card
                  key={tournament.id}
                  className="border-border/70 bg-card/80 shadow-sm transition hover:shadow-lg"
                >
                  <CardHeader className="space-y-4">
                    <div className="flex items-center justify-between gap-4">
                      <Badge variant="secondary" className="capitalize">
                        {formatDivision(tournament.division)}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {formatDateRange(
                          tournament.startDate,
                          tournament.endDate,
                        )}
                      </span>
                    </div>
                    <CardTitle className="text-xl font-semibold">
                      <Link href={`/tournaments/${tournament.slug}`}>
                        {tournament.name}
                      </Link>
                    </CardTitle>
                    <CardDescription>
                      {tournament.venue.city}, {tournament.venue.country}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                      <span>
                        Teams:{" "}
                        <strong className="text-foreground">
                          {tournament.teams.length}
                        </strong>
                      </span>
                      {tournament.standings ? (
                        <span>
                          Leader:{" "}
                          <strong className="text-foreground">
                            {
                              tournament.standings.find(
                                (standing) => standing.rank === 1,
                              )?.teamId
                            }
                          </strong>
                        </span>
                      ) : null}
                    </div>
                    <Link
                      href={`/tournaments/${tournament.slug}`}
                      className="inline-flex text-sm font-medium text-primary underline-offset-4 hover:underline"
                    >
                      View tournament →
                    </Link>
                  </CardContent>
                </Card>
              ))}
              {grouped[status].length === 0 ? (
                <Card className="border-dashed bg-background/60 text-muted-foreground">
                  <CardContent className="py-12 text-center text-sm">
                    No tournaments in this category yet. Stay tuned!
                  </CardContent>
                </Card>
              ) : null}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}

