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

export default async function PlayersPage() {
  const api = getApiClient();
  let players = [];
  
  try {
    players = await api.listPlayers();
  } catch (error) {
    console.error("Failed to fetch players from API, using mocks:", error);
    const mockApi = createMockApiClient();
    players = await mockApi.listPlayers();
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
      <header className="space-y-4">
        <h1 className="text-4xl font-semibold tracking-tight">Players</h1>
        <p className="max-w-3xl text-base text-muted-foreground">
          Track individual athletes across clubs and seasons. Dive into assist
          leaders, defensive standouts, and rising stars.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {players.map((player) => (
          <Card key={player.id} className="border-border/70 bg-card/80 shadow-sm">
            <CardHeader className="space-y-3">
              <div className="flex items-center justify-between">
                <Badge variant="outline">#{player.jerseyNumber ?? "—"}</Badge>
                <span className="text-xs text-muted-foreground">
                  {player.nationality ?? "PL"}
                </span>
              </div>
              <CardTitle className="text-xl font-semibold">
                <Link href={`/players/${player.id}`}>
                  {player.name.display}
                </Link>
              </CardTitle>
              <CardDescription>{player.pronouns ?? ""}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p>
                Club:{" "}
                {player.clubHistory.at(-1)?.teamName ?? "Club history coming soon"}
              </p>
              {player.stats ? (
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div>
                    <p className="font-semibold text-foreground">
                      {player.stats.totalGoals}
                    </p>
                    <p>Goals</p>
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">
                      {player.stats.totalAssists}
                    </p>
                    <p>Assists</p>
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">
                      {player.stats.totalDs}
                    </p>
                    <p>Ds</p>
                  </div>
                </div>
              ) : (
                <p>Stats will appear after the first tournament.</p>
              )}
              <Link
                href={`/players/${player.id}`}
                className="inline-flex text-sm font-medium text-primary underline-offset-4 hover:underline"
              >
                View profile →
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

