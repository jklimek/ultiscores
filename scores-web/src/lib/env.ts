export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  liveWsUrl:
    process.env.NEXT_PUBLIC_LIVE_WS_URL ?? "ws://localhost:8000/ws/matches",
};

