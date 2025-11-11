"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { Timeline } from "@/components/ui/timeline";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  type Match,
  type MatchEvent,
  type Team,
} from "@/lib/api/schemas";
import { formatDateTime } from "@/lib/format";

type MatchControlPanelProps = {
  match: Match;
  homeTeam: Team;
  awayTeam: Team;
};

type EventFormState = {
  teamId: string;
  type: MatchEvent["type"];
  primaryPlayerId: string;
  secondaryPlayerId: string;
  description: string;
  turnoverType?: string;
  timeoutType?: string;
};

const defaultEventForm = (teamId: string): EventFormState => ({
  teamId,
  type: "goal",
  primaryPlayerId: "",
  secondaryPlayerId: "",
  description: "",
});

function uniquePlayers(team: Team) {
  const map = new Map<string, Team["roster"][number]["player"]>();
  team.roster.forEach((entry) => {
    map.set(entry.player.id, entry.player);
  });
  return Array.from(map.values());
}

const eventTypeOptions: Array<{
  value: MatchEvent["type"];
  label: string;
}> = [
  { value: "goal", label: "Goal" },
  { value: "turnover", label: "Turnover" },
  { value: "timeout", label: "Timeout" },
  { value: "call", label: "Call" },
  { value: "pull", label: "Pull" },
  { value: "period", label: "Period" },
];

type TurnoverEvent = Extract<MatchEvent, { type: "turnover" }>;
type TimeoutEvent = Extract<MatchEvent, { type: "timeout" }>;

const turnoverOptions: Array<{ value: TurnoverEvent["turnoverType"]; label: string }> = [
  { value: "block", label: "Block" },
  { value: "throwaway", label: "Throwaway" },
  { value: "drop", label: "Drop" },
  { value: "stall", label: "Stall-out" },
  { value: "callahan", label: "Callahan" },
  { value: "unknown", label: "Other" },
];

const timeoutOptions: Array<{ value: TimeoutEvent["timeoutType"]; label: string }> = [
  { value: "team", label: "Team" },
  { value: "official", label: "Official" },
  { value: "spirit", label: "Spirit" },
];

type PlayerSelectProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  players: Array<Team["roster"][number]["player"]>;
  placeholder?: string;
  optional?: boolean;
};

function PlayerSelect({
  label,
  value,
  onChange,
  players,
  placeholder = "Select player",
  optional = false,
}: PlayerSelectProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        event.target instanceof Node &&
        !containerRef.current.contains(event.target)
      ) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const filteredPlayers = useMemo(() => {
    return players.filter((player) =>
      player.name.display.toLowerCase().includes(query.toLowerCase()),
    );
  }, [players, query]);

  const selectedPlayer = value
    ? players.find((player) => player.id === value)
    : undefined;

  return (
    <div className="flex flex-col gap-2" ref={containerRef}>
      <label className="text-xs font-semibold uppercase text-muted-foreground">
        {label}
      </label>
      <div className="relative">
        <Button
          type="button"
          variant="outline"
          className="flex h-11 w-full items-center justify-between rounded-xl border-border/60 bg-background px-3 text-left text-sm"
          onClick={() => setOpen((prev) => !prev)}
        >
          {selectedPlayer ? selectedPlayer.name.display : optional ? "Optional" : placeholder}
          <span className="ml-2 text-xs text-muted-foreground">▾</span>
        </Button>
        {open ? (
          <div className="absolute z-20 mt-2 w-full rounded-xl border border-border/70 bg-card shadow-lg">
            <div className="border-b border-border/60 px-3 py-2">
              <input
                autoFocus
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search player..."
                className="w-full rounded-lg border border-border/50 bg-background px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
            </div>
            <div className="max-h-56 overflow-y-auto px-1 py-2 text-sm">
              {optional ? (
                <button
                  type="button"
                  className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left hover:bg-muted ${
                    value === "" ? "bg-muted/70" : ""
                  }`}
                  onClick={() => {
                    onChange("");
                    setOpen(false);
                  }}
                >
                  None
                </button>
              ) : null}
              {filteredPlayers.length > 0 ? (
                filteredPlayers.map((player) => (
                  <button
                    type="button"
                    key={player.id}
                    className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left hover:bg-muted ${
                      value === player.id ? "bg-muted/70" : ""
                    }`}
                    onClick={() => {
                      onChange(player.id);
                      setOpen(false);
                      setQuery("");
                    }}
                  >
                    <span>{player.name.display}</span>
                    {player.jerseyNumber ? (
                      <span className="text-xs text-muted-foreground">
                        #{player.jerseyNumber}
                      </span>
                    ) : null}
                  </button>
                ))
              ) : (
                <p className="px-3 py-2 text-xs text-muted-foreground">
                  No players match “{query}”
                </p>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function MatchControlPanel({
  match,
  homeTeam,
  awayTeam,
}: MatchControlPanelProps) {
  const [connectionStatus, setConnectionStatus] =
    useState<"connecting" | "connected" | "disconnected">("connecting");
  const [localMatch, setLocalMatch] = useState(match);
  const [events, setEvents] = useState(match.events ?? []);
  const [eventForm, setEventForm] = useState<EventFormState>(
    defaultEventForm(match.home.teamId),
  );
  const [notes, setNotes] = useState("");

  const homePlayers = useMemo(() => uniquePlayers(homeTeam), [homeTeam]);
  const awayPlayers = useMemo(() => uniquePlayers(awayTeam), [awayTeam]);

  const getOpponentTeamId = (teamId: string) =>
    teamId === homeTeam.id ? awayTeam.id : homeTeam.id;

  useEffect(() => {
    const timer = setTimeout(() => setConnectionStatus("connected"), 600);
    return () => clearTimeout(timer);
  }, []);

  const scoreboard = {
    home: localMatch.home,
    away: localMatch.away,
  };

  const handleAdjustScore = (side: "home" | "away", delta: number) => {
    setLocalMatch((prev) => ({
      ...prev,
      [side]: {
        ...prev[side],
        score: Math.max(prev[side].score + delta, 0),
      },
    }));
  };

  const handleTimeout = (team: "home" | "away") => {
    setLocalMatch((prev) => ({
      ...prev,
      [team]: {
        ...prev[team],
        timeoutsRemaining: Math.max(prev[team].timeoutsRemaining - 1, 0),
      },
    }));
  };

  const handleEventSubmit = () => {
    const currentTeamId = eventForm.teamId;
    const id =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `local-${Date.now()}`;

    const baseEvent: MatchEvent = {
      id,
      type: eventForm.type,
      sequence: events.length + 1,
      point:
        eventForm.type === "goal"
          ? scoreboard[eventForm.teamId === match.home.teamId ? "home" : "away"]
              .score + 1
          : scoreboard.home.score + scoreboard.away.score,
      elapsedSeconds: 0,
      clockLabel: null,
      teamId: eventForm.teamId,
      createdAt: new Date().toISOString(),
      summary: eventForm.description || undefined,
      ...(eventForm.type === "goal"
        ? {
            scorerId: eventForm.primaryPlayerId,
            assisterId: eventForm.secondaryPlayerId || null,
            offensiveLine: [
              eventForm.primaryPlayerId,
              eventForm.secondaryPlayerId,
            ].filter(Boolean),
          }
        : eventForm.type === "turnover"
          ? {
              turnoverType: (eventForm.turnoverType as TurnoverEvent["turnoverType"]) ??
                "unknown",
              causedById: eventForm.primaryPlayerId || null,
              reason: eventForm.description || undefined,
            }
          : eventForm.type === "timeout"
            ? {
                timeoutType:
                  (eventForm.timeoutType as TimeoutEvent["timeoutType"]) ?? "team",
              }
            : eventForm.type === "call"
              ? {
                  callType: "foul" as const,
                  resolved: true,
                }
              : eventForm.type === "pull"
                ? {
                    pullingTeamId: eventForm.teamId,
                  }
                : eventForm.type === "period"
                  ? {
                      label: eventForm.description || "Period update",
                    }
                  : {}),
    } as MatchEvent;

    setEvents((prev) => [...prev, baseEvent]);
    const shouldSwitch =
      baseEvent.type === "goal" ||
      baseEvent.type === "turnover" ||
      baseEvent.type === "pull";
    const nextTeamId = shouldSwitch
      ? getOpponentTeamId(currentTeamId)
      : currentTeamId;
    setEventForm(defaultEventForm(nextTeamId));
    // TODO: integrate with FastAPI mutations
    console.info("Event logged (mock)", baseEvent);
  };

  const timelineItems = events
    .slice()
    .reverse()
    .map((event) => {
      const tone: "goal" | "turnover" | "timeout" | "default" =
        event.type === "goal"
          ? "goal"
          : event.type === "turnover"
            ? "turnover"
            : event.type === "timeout"
              ? "timeout"
              : "default";

      return {
        id: event.id,
        timeLabel: event.clockLabel ?? formatDateTime(event.createdAt),
        title:
          event.type === "goal"
            ? `Goal by ${event.scorerId}`
            : event.type === "turnover"
              ? `Turnover (${event.turnoverType})`
              : event.type === "timeout"
                ? `Timeout (${event.timeoutType})`
                : event.type === "period"
                  ? event.label
                  : event.summary ?? event.type,
        description: event.summary,
        teamName:
          event.teamId === match.home.teamId
            ? homeTeam.shortName
            : event.teamId === match.away.teamId
              ? awayTeam.shortName
              : undefined,
        tone,
      };
    });

  const availablePlayers =
    eventForm.teamId === homeTeam.id ? homePlayers : awayPlayers;

  const handleTeamClick = (teamId: string) => {
    setEventForm((prev) => ({
      ...prev,
      teamId,
    }));
  };

  const handleEventTypeClick = (type: MatchEvent["type"]) => {
    setEventForm((prev) => ({
      ...prev,
      type,
      turnoverType: type === "turnover" ? prev.turnoverType ?? "block" : undefined,
      timeoutType: type === "timeout" ? prev.timeoutType ?? "team" : undefined,
    }));
  };

  const handleTurnoverTypeClick = (value: TurnoverEvent["turnoverType"]) => {
    setEventForm((prev) => ({
      ...prev,
      turnoverType: value,
    }));
  };

  const handleTimeoutTypeClick = (value: TimeoutEvent["timeoutType"]) => {
    setEventForm((prev) => ({
      ...prev,
      timeoutType: value,
    }));
  };

  const handleUndo = () => {
    setEvents((prev) => prev.slice(0, -1));
  };

  return (
    <div className="space-y-8">
      <Card className="border-primary/40 bg-card/80">
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <CardTitle className="text-2xl font-semibold">
                {homeTeam.name} vs {awayTeam.name}
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Field {match.fieldLabel ?? match.fieldId ?? "TBC"} •{" "}
                {formatDateTime(match.startTime)} • {match.round}
              </p>
            </div>
            <span
              className="inline-flex items-center rounded-full border border-border/60 bg-background px-3 py-1 text-xs font-medium"
              data-status={connectionStatus}
            >
              <span
                className={`mr-2 inline-block h-2 w-2 rounded-full ${
                  connectionStatus === "connected"
                    ? "bg-emerald-500"
                    : connectionStatus === "connecting"
                      ? "bg-amber-500"
                      : "bg-rose-500"
                }`}
              />
              {connectionStatus === "connected"
                ? "Connected to live feed"
                : connectionStatus === "connecting"
                  ? "Connecting..."
                  : "Disconnected"}
            </span>
          </div>
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="grid gap-6 rounded-3xl border border-border/70 bg-background/80 p-6">
            <div className="grid gap-4 sm:grid-cols-2">
              {(["home", "away"] as const).map((side) => {
                const team = side === "home" ? homeTeam : awayTeam;
                const state = scoreboard[side];
                const isSelected = eventForm.teamId === team.id;
                return (
                  <div
                    key={side}
                    className={`flex flex-col gap-3 rounded-2xl border border-border/70 bg-card/80 p-4 shadow-inner ${
                      isSelected ? "ring-2 ring-primary/50" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() => handleTeamClick(team.id)}
                        className="text-left text-sm font-semibold tracking-tight hover:underline"
                      >
                        {team.name}
                      </button>
                      <span className="text-xs uppercase text-muted-foreground">
                        Timeouts {state.timeoutsRemaining}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Button
                          size="icon"
                          variant="outline"
                          onClick={() => handleAdjustScore(side, -1)}
                        >
                          −
                        </Button>
                        <span className="text-3xl font-semibold">
                          {state.score}
                        </span>
                        <Button
                          size="icon"
                          variant="outline"
                          onClick={() => handleAdjustScore(side, 1)}
                        >
                          +
                        </Button>
                      </div>
                      <Button
                        variant="secondary"
                        onClick={() => handleTimeout(side)}
                        disabled={state.timeoutsRemaining === 0}
                      >
                        Use timeout
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>

            <Separator />

            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">
                    Team
                  </span>
                  <div className="flex gap-2">
                    {[homeTeam, awayTeam].map((team) => {
                      const isActive = eventForm.teamId === team.id;
                      return (
                        <Button
                          key={team.id}
                          type="button"
                          variant={isActive ? "default" : "outline"}
                          className="flex-1 rounded-xl"
                          onClick={() => handleTeamClick(team.id)}
                        >
                          {team.shortName ?? team.name}
                        </Button>
                      );
                    })}
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">
                    Event type
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {eventTypeOptions.map((option) => {
                      const isActive = eventForm.type === option.value;
                      return (
                        <Button
                          key={option.value}
                          type="button"
                          variant={isActive ? "default" : "outline"}
                          className="rounded-xl text-xs sm:text-sm"
                          onClick={() => handleEventTypeClick(option.value)}
                        >
                          {option.label}
                        </Button>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <PlayerSelect
                  label="Primary player"
                  value={eventForm.primaryPlayerId}
                  onChange={(playerId) =>
                    setEventForm((prev) => ({
                      ...prev,
                      primaryPlayerId: playerId,
                    }))
                  }
                  players={availablePlayers}
                  placeholder="Select player"
                />
                <PlayerSelect
                  label="Secondary player"
                  value={eventForm.secondaryPlayerId}
                  onChange={(playerId) =>
                    setEventForm((prev) => ({
                      ...prev,
                      secondaryPlayerId: playerId,
                    }))
                  }
                  players={availablePlayers}
                  placeholder="Assist / block"
                  optional
                />
              </div>

              {eventForm.type === "turnover" ? (
                <div className="flex flex-col gap-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">
                    Turnover type
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {turnoverOptions.map((option) => {
                      const isActive = eventForm.turnoverType === option.value;
                      return (
                        <Button
                          key={option.value}
                          type="button"
                          variant={isActive ? "default" : "outline"}
                          className="rounded-xl text-xs sm:text-sm"
                          onClick={() => handleTurnoverTypeClick(option.value)}
                        >
                          {option.label}
                        </Button>
                      );
                    })}
                  </div>
                </div>
              ) : null}

              {eventForm.type === "timeout" ? (
                <div className="flex flex-col gap-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">
                    Timeout type
                  </span>
                  <div className="flex gap-2">
                    {timeoutOptions.map((option) => {
                      const isActive = eventForm.timeoutType === option.value;
                      return (
                        <Button
                          key={option.value}
                          type="button"
                          variant={isActive ? "default" : "outline"}
                          className="rounded-xl text-xs sm:text-sm"
                          onClick={() => handleTimeoutTypeClick(option.value)}
                        >
                          {option.label}
                        </Button>
                      );
                    })}
                  </div>
                </div>
              ) : null}

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold uppercase text-muted-foreground">
                  Description / notes
                </label>
                <textarea
                  rows={3}
                  className="rounded-xl border border-border/60 bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                  value={eventForm.description}
                  onChange={(event) =>
                    setEventForm((prev) => ({
                      ...prev,
                      description: event.target.value,
                    }))
                  }
                />
              </div>

              <div className="flex justify-end">
                <Button onClick={handleEventSubmit}>Log event</Button>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <label className="text-xs font-semibold uppercase text-muted-foreground">
                Scorer notes
              </label>
              <textarea
                rows={2}
                placeholder="Quick reminders, spirit conversations, weather alerts..."
                className="rounded-xl border border-border/60 bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
              />
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setNotes("")}>
                  Clear
                </Button>
                <Button variant="secondary" disabled>
                  Sync notes (mock)
                </Button>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-border/70 bg-background/80 p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Event timeline</h3>
              <span className="text-xs text-muted-foreground">
                {events.length} entries
              </span>
            </div>
            <Separator className="my-4" />
            <ScrollArea className="h-[420px] pr-2">
              {timelineItems.length > 0 ? (
                <Timeline items={timelineItems} />
              ) : (
                <p className="text-sm text-muted-foreground">
                  Logged events will appear here in real time.
                </p>
              )}
            </ScrollArea>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={handleUndo} disabled={events.length === 0}>
          Undo last event
        </Button>
        <Button variant="secondary" disabled>
          Publish to fans (mock)
        </Button>
      </div>
    </div>
  );
}

