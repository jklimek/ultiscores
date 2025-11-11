import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

type PlayerPageProps = {
  params: Promise<{ playerId: string }>;
};

export default async function PlayerPage({ params }: PlayerPageProps) {
  const { playerId } = await params;
  const api = getApiClient();

  let player;
  try {
    player = await api.getPlayer(playerId);
  } catch {
    notFound();
  }

  const latestTeam = player.clubHistory.at(-1);

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
      <header className="space-y-6 rounded-3xl border border-border/60 bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <Badge variant="secondary">#{player.jerseyNumber ?? "—"}</Badge>
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              {player.name.display}
            </h1>
            <p className="text-sm text-muted-foreground">
              {player.pronouns ?? ""}{" "}
              {latestTeam
                ? `• ${latestTeam.teamName} (${latestTeam.season})`
                : ""}
            </p>
          </div>
          <div className="text-right text-sm text-muted-foreground">
            <p>Nationality: {player.nationality ?? "PL"}</p>
            <p>Throws: {player.throws ?? "unknown"}</p>
            <p>Roles: {player.roles.join(", ") || "—"}</p>
          </div>
        </div>
        {player.stats ? (
          <div className="grid gap-4 sm:grid-cols-4">
            <div className="rounded-2xl border border-border/70 bg-background/70 p-4 text-center">
              <p className="text-sm text-muted-foreground">Goals</p>
              <p className="mt-2 text-2xl font-semibold">
                {player.stats.totalGoals}
              </p>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/70 p-4 text-center">
              <p className="text-sm text-muted-foreground">Assists</p>
              <p className="mt-2 text-2xl font-semibold">
                {player.stats.totalAssists}
              </p>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/70 p-4 text-center">
              <p className="text-sm text-muted-foreground">Defensive plays</p>
              <p className="mt-2 text-2xl font-semibold">
                {player.stats.totalDs}
              </p>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/70 p-4 text-center">
              <p className="text-sm text-muted-foreground">Points played</p>
              <p className="mt-2 text-2xl font-semibold">
                {player.stats.totalPointsPlayed}
              </p>
            </div>
          </div>
        ) : null}
      </header>

      <Tabs defaultValue="history">
        <TabsList>
          <TabsTrigger value="history">Club history</TabsTrigger>
          <TabsTrigger value="bio">Profile</TabsTrigger>
        </TabsList>

        <TabsContent value="history" className="mt-8">
          <Card className="border-border/70">
            <CardHeader>
              <CardTitle className="text-xl">Team journey</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-hidden rounded-3xl border border-border/60">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Season</TableHead>
                      <TableHead>Team</TableHead>
                      <TableHead>Division</TableHead>
                      <TableHead>Tournament</TableHead>
                      <TableHead>Placement</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {player.clubHistory.flatMap((entry) =>
                      entry.tournaments.map((tournament) => (
                        <TableRow key={`${entry.teamId}-${tournament.tournamentId}`}>
                          <TableCell>{entry.season}</TableCell>
                          <TableCell>{entry.teamName}</TableCell>
                          <TableCell className="capitalize">
                            {entry.division}
                          </TableCell>
                          <TableCell>{tournament.tournamentName}</TableCell>
                          <TableCell>
                            {tournament.placement ?? "—"}
                          </TableCell>
                        </TableRow>
                      )),
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bio" className="mt-8">
          <Card className="border-border/70">
            <CardHeader>
              <CardTitle className="text-xl">Player profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>Date of birth: {player.dateOfBirth ?? "—"}</p>
              <p>Height: {player.heightCm ? `${player.heightCm} cm` : "—"}</p>
              <p>
                Dominant positions:{" "}
                {player.dominantPositions.length > 0
                  ? player.dominantPositions.join(", ")
                  : "Flex"}
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

