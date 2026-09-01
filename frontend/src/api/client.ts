import type { RoutesResponse, TriageRequest, TriageResponse } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * fetch has no timeout of its own, so without this a stalled request leaves
 * someone watching a "Checking…" button indefinitely with nothing to act on.
 * Ten seconds is long enough for a slow connection and short enough that the
 * page admits defeat while the person is still paying attention.
 */
const TIMEOUT_MS = 10_000;

/**
 * Every failure the UI can encounter, in one shape. Components should never
 * see a raw fetch rejection or an HTTP status code.
 *
 * `invalid` carries a message the server wrote about what the person entered,
 * so it is safe to show them. `network` and `server` use our own wording,
 * because whatever went wrong there is not their problem to understand.
 */
export type ApiError = {
  kind: "network" | "server" | "invalid";
  message: string;
};

export type ApiResult<T> =
  { ok: true; data: T } | { ok: false; error: ApiError };

const NETWORK_ERROR: ApiError = {
  kind: "network",
  message: "We could not reach the service. Please try again.",
};

const TIMEOUT_ERROR: ApiError = {
  kind: "network",
  message: "The service is taking longer than expected. Please try again.",
};

const SERVER_ERROR: ApiError = {
  kind: "server",
  message: "Something went wrong at our end. Please try again.",
};

const UNREADABLE_ERROR: ApiError = {
  kind: "server",
  message: "We received an unexpected response. Please try again.",
};

const request = async <T>(
  path: string,
  body?: TriageRequest,
): Promise<ApiResult<T>> => {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: body ? "POST" : "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (cause) {
    const timedOut =
      cause instanceof DOMException && cause.name === "TimeoutError";
    return { ok: false, error: timedOut ? TIMEOUT_ERROR : NETWORK_ERROR };
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { ok: false, error: UNREADABLE_ERROR };
  }

  if (!response.ok) {
    // A 400 means the server rejected what was entered and wrote a plain
    // English reason. Anything else is our fault, not the person's.
    const message =
      response.status === 400 && isErrorPayload(payload)
        ? payload.message
        : undefined;
    return {
      ok: false,
      error: message ? { kind: "invalid", message } : SERVER_ERROR,
    };
  }

  return { ok: true, data: payload as T };
};

const isErrorPayload = (payload: unknown): payload is { message: string } =>
  typeof payload === "object" &&
  payload !== null &&
  "message" in payload &&
  typeof (payload as { message: unknown }).message === "string";

export const fetchRoutes = (): Promise<ApiResult<RoutesResponse>> =>
  request<RoutesResponse>("/api/triage/routes/");

export const submitTriage = (
  body: TriageRequest,
): Promise<ApiResult<TriageResponse>> =>
  request<TriageResponse>("/api/triage/", body);
