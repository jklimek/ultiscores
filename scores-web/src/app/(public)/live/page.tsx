import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getApiClient } from "@/lib/api/server";
import { formatDate } from "@/lib/format";
import { createMockApiClient } from "@/lib/api/mock-client";
import type { Match } from "@/lib/api/schemas";

export default async function LivePage() {
  const api = getApiClient();
  let matches: Match[] = [];
  try {
    matches = await api.listMatches();
  } catch {
    const mockApi = createMockApiClient();
    matches = await mockApi.listMatches();
  }

  const liveMatches = matches.filter((match) => match.status === "live");
  const displayMatches =
    liveMatches.length > 0
      ? liveMatches
      : matches.filter((match) => match.status === "final");

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <header className="space-y-3">
        <h1 className="text-4xl font-semibold tracking-tight">
          Live Centre
        </h1>
        <p className="max-w-3xl text-base text-muted-foreground">
          Follow current matches with play-by-play updates, score differentials,
          and key stats in one responsive dashboard.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        {displayMatches.length === 0 ? (
          <Card className="border-dashed bg-background/60 text-muted-foreground">
            <CardContent className="py-12 text-center text-sm">
              No live matches at the moment. Check back soon!
            </CardContent>
          </Card>
        ) : (
          displayMatches.map((match) => (
            <Card key={match.id} className="border-border/70">
              <CardHeader>
                <CardTitle className="text-lg">
                  {match.home.teamId} vs {match.away.teamId}
                </CardTitle>
                <p className="text-xs text-muted-foreground">
                  {formatDate(match.startTime)} • Field{" "}
                  {match.fieldLabel ?? match.fieldId ?? "TBC"}
                </p>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <div className="text-center">
                  <p className="text-3xl font-semibold">{match.home.score}</p>
                  <p className="text-xs text-muted-foreground">
                    {match.home.teamId}
                  </p>
                </div>
                <span className="text-xs uppercase tracking-wide text-muted-foreground">
                  {match.status}
                </span>
                <div className="text-center">
                  <p className="text-3xl font-semibold">{match.away.score}</p>
                  <p className="text-xs text-muted-foreground">
                    {match.away.teamId}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

