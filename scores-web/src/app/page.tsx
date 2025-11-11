import Link from "next/link";

import { Timeline } from "@/components/ui/timeline";
import { getApiClient } from "@/lib/api/server";
import { createMockApiClient } from "@/lib/api/mock-client";
import type { Match } from "@/lib/api/schemas";

export default async function Home() {
  const api = getApiClient();
  let tournaments = [];
  let matches: Match[] = [];
  let teams = [];

  try {
    [tournaments, matches, teams] = await Promise.all([
      api.listTournaments(),
      api.listMatches({ status: "final" }),
      api.listTeams(),
    ]);
  } catch (error) {
    console.error("Failed to fetch data from API, using mocks:", error);
    const mockApi = createMockApiClient();
    [tournaments, matches, teams] = await Promise.all([
      mockApi.listTournaments(),
      mockApi.listMatches({ status: "final" }),
      mockApi.listTeams(),
    ]);
  }

  const teamMap = new Map(teams.map((team) => [team.id, team.name]));
  const featuredTournament = tournaments.at(0);
  const featuredMatch = matches.at(0);
  const matchEvents = featuredMatch
    ? await api.listMatchEvents(featuredMatch.id)
    : [];

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-4 py-10 sm:px-6 lg:px-8">
      <section className="flex flex-col gap-6 lg:flex-row lg:items-center lg:gap-12">
        <div className="flex-1 space-y-6">
          <span className="inline-flex w-fit items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            Built by players, for players
          </span>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Share the story of every point in Ultimate. Together.
          </h1>
          <p className="max-w-2xl text-base text-muted-foreground sm:text-lg">
            Scores keeps the community in sync — sideline volunteers, travelling
            supporters, and teammates at home. Inspired by grassroots scoreboards
            and big-stage hubs like the European Beach Ultimate Club Championships
            live centre, we bring the same love of the game to every league day.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              className="inline-flex items-center justify-center rounded-full bg-primary px-6 py-2 text-sm font-medium text-primary-foreground transition hover:bg-primary/90"
              href="/live"
            >
              Follow live games
            </Link>
            <Link
              className="inline-flex items-center justify-center rounded-full border border-border px-6 py-2 text-sm font-medium text-foreground transition hover:border-primary hover:text-primary"
              href="/tournaments"
            >
              Browse tournaments
            </Link>
          </div>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-md rounded-3xl border border-border/60 bg-card p-6 shadow-lg shadow-primary/5">
            <h2 className="text-lg font-semibold">Live scoreboard</h2>
            <p className="text-sm text-muted-foreground">
              {featuredMatch
                ? `${teamMap.get(featuredMatch.home.teamId) ?? featuredMatch.home.teamId} vs ${teamMap.get(featuredMatch.away.teamId) ?? featuredMatch.away.teamId} — ${featuredMatch.fieldLabel ?? "Field TBC"}`
                : "Upcoming fixtures land here"}
            </p>
            <div className="mt-6 grid grid-cols-2 gap-4 text-center">
              <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
                <p className="text-sm uppercase tracking-wide text-muted-foreground">
                  {featuredMatch
                    ? teamMap.get(featuredMatch.home.teamId) ??
                      featuredMatch.home.teamId
                    : "TBD"}
                </p>
                <p className="mt-2 text-4xl font-semibold">
                  {featuredMatch ? featuredMatch.home.score : "—"}
                </p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
                <p className="text-sm uppercase tracking-wide text-muted-foreground">
                  {featuredMatch
                    ? teamMap.get(featuredMatch.away.teamId) ??
                      featuredMatch.away.teamId
                    : "TBD"}
                </p>
                <p className="mt-2 text-4xl font-semibold">
                  {featuredMatch ? featuredMatch.away.score : "—"}
                </p>
              </div>
            </div>
            <Timeline
              className="mt-6 text-sm"
              items={
                matchEvents.slice(0, 4).map((event) => ({
                  id: event.id,
                  timeLabel: event.clockLabel ?? `${Math.round(event.elapsedSeconds / 60)}'`,
                  title:
                    event.type === "goal"
                      ? `Goal — ${event.scorerId}`
                      : event.type === "turnover"
                        ? `Turnover — ${event.reason ?? event.turnoverType}`
                        : event.type === "timeout"
                          ? `Timeout — ${event.timeoutType}`
                          : event.type === "period"
                            ? event.label
                            : event.summary ?? event.type,
                  description: event.summary,
                  teamName: event.teamId ?? undefined,
                  tone:
                    event.type === "goal"
                      ? "goal"
                      : event.type === "turnover"
                        ? "turnover"
                        : event.type === "timeout"
                          ? "timeout"
                          : "default",
                })) ?? []
              }
            />
          </div>
        </div>
      </section>
      <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[
          {
            title: "Scorekeeping made friendly",
            description:
              "Large buttons, quick player search, and live timelines keep sideline crews focused on the action — not on wrestling with forms.",
          },
          {
            title: "Club memories in one place",
            description:
              "Follow your team’s story across seasons, keep rosters tidy, and revisit that final with everyone who threw, caught, or layout-blocked.",
          },
          {
            title: "Community-first design",
            description:
              "Mobile-first for muddy sidelines, beautiful on the big screen back home, and open to contributors who want to keep Ultimate thriving.",
          },
        ].map((feature) => (
          <div
            key={feature.title}
            className="rounded-3xl border border-border/70 bg-card p-6 shadow-inner shadow-black/5"
          >
            <h3 className="text-xl font-semibold">{feature.title}</h3>
            <p className="mt-3 text-sm text-muted-foreground">
              {feature.description}
            </p>
          </div>
        ))}
      </section>
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-border/70 bg-card p-6">
          <h3 className="text-xl font-semibold">Built for Polish Ultimate</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Inspired by the heritage of{" "}
            <a
              href="https://scores.frisbee.pl/"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-primary underline-offset-2 hover:underline"
            >
              scores.frisbee.pl
            </a>
            {" "}
            and international showcases like{" "}
            <a
              href="https://live.ebucc.eu/"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-primary underline-offset-2 hover:underline"
            >
              the EBUCC live centre
            </a>
            , modernised with open tools and a welcoming interface.
          </p>
        </div>
        <div className="rounded-3xl border border-border/70 bg-card p-6">
          <h3 className="text-xl font-semibold">Integrate your data layer</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            This UI is ready to connect with a FastAPI backend that serves live
            tournaments, match events, rosters, and more. Mock endpoints power
            prototyping today while the production APIs take shape.
          </p>
          {featuredTournament ? (
            <p className="mt-4 text-xs text-muted-foreground">
              Currently previewing: {featuredTournament.name} (
              {featuredTournament.startDate} → {featuredTournament.endDate})
            </p>
          ) : null}
        </div>
      </section>
    </div>
  );
}
