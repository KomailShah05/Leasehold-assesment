import { useCallback, useEffect, useState } from "react";
import type { ApiError } from "../api/client";
import { fetchRoutes, submitTriage } from "../api/client";
import type {
  RoutesResponse,
  TriageRequest,
  TriageResponse,
} from "../api/types";

/**
 * The whole journey's state and every call to the API, in one place.
 *
 * Pulling this out of App leaves the components with nothing to do but render
 * what they are given, and gives the behaviour a seam that can be tested
 * without mounting the page.
 */
export const useTriage = () => {
  const [routes, setRoutes] = useState<RoutesResponse | null>(null);
  const [result, setResult] = useState<TriageResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);
  // What was last sent, so a follow-up answer carries the original scenario or
  // description, and so a failed request can be retried without making someone
  // type it all again. The API stays stateless; the browser holds the thread.
  const [lastRequest, setLastRequest] = useState<TriageRequest | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchRoutes().then((response) => {
      if (cancelled) return;
      if (response.ok) setRoutes(response.data);
      else setError(response.error);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const send = useCallback(async (body: TriageRequest) => {
    setBusy(true);
    setError(null);
    setLastRequest(body);
    const response = await submitTriage(body);
    setBusy(false);
    if (response.ok) setResult(response.data);
    else setError(response.error);
  }, []);

  const start = useCallback(
    (choice: { scenario?: string; description?: string }) => void send(choice),
    [send],
  );

  const answer = useCallback(
    (answerId: string) => {
      if (lastRequest === null) return;
      void send({ ...lastRequest, answerId });
    },
    [lastRequest, send],
  );

  const retry = useCallback(() => {
    if (lastRequest === null) return;
    void send(lastRequest);
  }, [lastRequest, send]);

  const restart = useCallback(() => {
    setResult(null);
    setError(null);
    setLastRequest(null);
  }, []);

  return {
    routes,
    result,
    error,
    busy,
    canRetry: lastRequest !== null,
    start,
    answer,
    retry,
    restart,
  };
};
