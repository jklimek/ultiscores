# Scores Web Architecture

## Frontend Stack

- **Next.js 16 · App Router** with React Server Components for data fetching and layout composition.
- **TypeScript + Tailwind CSS 4** for strict typing and responsive design tokens.
- **shadcn/ui design system** providing reusable primitives (buttons, cards, tabs, tables, timeline).
- **next-themes** for synchronized light/dark themes across the app and Storybook.
- **Vitest + Testing Library** for unit and DOM testing, Storybook (Vite builder) for component documentation.

## Directory Layout

```
src/
  app/                    # Next.js routes
    (public)/             # Public surfaces (tournaments, teams, players, live hub)
    (admin)/              # Organizer workspace (match control panel)
    layout.tsx            # Global ThemeProvider + AppShell navigation
  components/
    admin/                # Live scoring control UI
    layout/               # App-wide shell, toggles, navigation
    ui/                   # Reusable design system elements (shadcn + custom timeline)
  lib/
    api/                  # Zod schemas, API client, realtime message contracts, mock data
    env.ts                # Runtime environment helpers
    format.ts             # Date/division formatting helpers
    utils.ts              # Tailwind class merge helpers
```

## Data Flow

1. **`lib/api/schemas.ts`** defines Zod contracts for tournaments, matches, events, teams, players, and websocket payloads.
2. **`createApiClient`** wraps the FastAPI REST endpoints with typed fetch helpers, handling caching & error surfacing.
3. **`createMockApiClient`** provides deterministic mock data for local development until the FastAPI backend is ready.
4. Route handlers (server components) call `getApiClient()` to select the real or mock client based on environment hints.
5. Client components like the admin match control panel consume typed props and orchestrate optimistic UI interactions.

## Live Scoring Workspace

- `/admin/matches/[matchId]` renders `MatchControlPanel`.
- Features: score adjustments, timeout tracking, event logging form, notes, and timeline review.
- Currently operates in mock mode while websocket + mutation endpoints are implemented; integration points are marked with TODO comments.

## Quality & DX

- `npm run lint` / `npm run test` enforce ESLint (Next.js strict rules) and Vitest suites.
- `npm run storybook` spins up Storybook with Tailwind and theming decorators. Sample stories exist for UI primitives (e.g. `Timeline`).
- `docs/api-contracts.md` documents REST + websocket contracts expected from the FastAPI backend.
- `docs/architecture.md` (this file) captures high-level decisions for onboarding contributors.

## Next Steps

1. Wire the API client to the FastAPI services and replace mock data.
2. Implement websocket subscriptions in `MatchControlPanel` (using `env.liveWsUrl`).
3. Expand Vitest coverage for domain utilities and add Storybook stories for complex layouts (tournament detail, admin forms).

