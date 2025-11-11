# API Contracts

This document describes the FastAPI endpoints and websocket channels that the Scores web UI expects. All responses are JSON unless stated otherwise.

## REST Endpoints

### Seasons

- `GET /v1/seasons`
  - Returns a collection of season summaries (`SeasonSummary[]`).
  - Optional query params: none.

### Tournaments

- `GET /v1/tournaments`
  - Query params:
    - `seasonId`: filter by season identifier.
    - `division`: `open | women | mixed | junior | masters`.
    - `status`: `upcoming | in_progress | completed | cancelled`.
    - `search`: case-insensitive substring on tournament name.
  - Response: paginated collection of `Tournament`.

- `GET /v1/tournaments/{tournamentId}`
  - Response: single `Tournament` object including stages, pools, standings.

- `GET /v1/tournaments/{tournamentId}/spirit`
  - Response: collection of `SpiritScore` entries for matches in the tournament.

### Matches

- `GET /v1/matches`
  - Query params:
    - `tournamentId`
    - `teamId`
    - `division`
    - `status`: `scheduled | live | final`
  - Response: paginated list of `Match` objects (without event timelines).

- `GET /v1/matches/{matchId}`
  - Response: full `Match` object including event timeline.

- `GET /v1/matches/{matchId}/events`
  - Response: ordered collection of `MatchEvent`.

### Teams

- `GET /v1/teams`
  - Query params:
    - `seasonId`
    - `division`
    - `search`
  - Response: paginated list of `Team` objects (rosters grouped by tournament).

- `GET /v1/teams/{teamId}`
  - Response: single `Team` with tournament history and roster.

### Players

- `GET /v1/players`
  - Query params:
    - `teamId`
    - `tournamentId`
    - `search`
  - Response: paginated list of `Player` objects.

- `GET /v1/players/{playerId}`
  - Response: single `Player` with club history and cumulative stats.

## Live Scoring Websocket

- Endpoint: `GET ws://.../ws/matches/{matchId}`
- Messages follow the discriminated union in `liveMessageSchema`:
  - `connection_ack` – sent after handshake (contains `heartbeatInterval`).
  - `match_snapshot` – full `Match` payload for replay.
  - `score_update` – minimal scoreboard updates.
  - `event_created` – append-only match events.
  - `timeout_taken` – team timeout adjustments.
  - `spirit_updated` – spirit sheet submission notification.
  - `error` – error details (recoverable or fatal).
- Clients should send heartbeats every `heartbeatInterval` milliseconds and may push organiser actions via a complementary authenticated channel (defined during backend implementation).

## Authentication (Future Work)

- Authenticated organiser routes will live under `/v1/admin/**`.
- Expected flows:
  - `POST /v1/admin/matches/{matchId}/events`
  - `PATCH /v1/admin/matches/{matchId}` (score corrections, caps, etc.)
  - `POST /v1/admin/tournaments/{tournamentId}/publish`

These routes will require token-based authentication (Auth.js or FastAPI JWT) and are **not** yet consumed by the UI.

