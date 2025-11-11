import "server-only";

import { createApiClient } from "@/lib/api/client";
import { createMockApiClient } from "@/lib/api/mock-client";

const mockPreference = process.env.NEXT_PUBLIC_USE_API_MOCKS;

const shouldUseMockData =
  mockPreference !== "false" &&
  mockPreference !== "0";

export function getApiClient() {
  if (shouldUseMockData) {
    return createMockApiClient();
  }
  return createApiClient();
}

