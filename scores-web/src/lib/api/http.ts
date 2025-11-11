import "server-only";

import { env } from "@/lib/env";
import { type ZodType } from "zod";

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

type ApiFetchInit = Omit<RequestInit, "body"> & {
  body?: Record<string, unknown> | FormData;
  revalidate?: number | false;
};

async function parseResponse<T>(
  response: Response,
  schema: ZodType<T>,
): Promise<T> {
  const data = await response.json();
  const parsed = schema.safeParse(data);

  if (!parsed.success) {
    throw new ApiError("Failed to parse API response", response.status, {
      issues: parsed.error.issues,
    });
  }

  return parsed.data as T;
}

export async function apiFetch<T>(
  path: string,
  schema: ZodType<T>,
  init: ApiFetchInit = {},
): Promise<T> {
  const { body, revalidate, headers, ...fetchInit } = init;

  const requestHeaders = new Headers(headers);
  requestHeaders.set("Accept", "application/json");
  if (!(body instanceof FormData)) {
    requestHeaders.set("Content-Type", "application/json");
  }

  const url = new URL(path, env.apiBaseUrl);
  const nextOptions =
    revalidate === false ? undefined : { revalidate };

  const response = await fetch(url.toString(), {
    ...fetchInit,
    cache: revalidate === false ? "no-store" : fetchInit.cache,
    headers: requestHeaders,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    next: nextOptions,
  });

  if (!response.ok) {
    let details: unknown;
    try {
      details = await response.json();
    } catch {
      // ignore parsing error
    }
    throw new ApiError(response.statusText, response.status, details);
  }

  return parseResponse<T>(response, schema);
}

