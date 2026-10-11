import { useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/endpoints";
import { ApiError } from "@/lib/api/client";

const MIN = 60_000;

/** Stable query key factory. `all` prefixes everything for bulk invalidation. */
export const queryKeys = {
  all: ["api"] as const,
  health: () => [...queryKeys.all, "health"] as const,
  portfolio: () => [...queryKeys.all, "portfolio"] as const,
  positions: () => [...queryKeys.all, "positions"] as const,
  history: (days: number) => [...queryKeys.all, "history", days] as const,
  positionHistory: (ticker: string) => [...queryKeys.all, "positions", ticker, "history"] as const,
  monthlyReturns: () => [...queryKeys.all, "monthly-returns"] as const,
  analytics: () => [...queryKeys.all, "analytics"] as const,
  latestReport: () => [...queryKeys.all, "report", "latest"] as const,
  news: () => [...queryKeys.all, "news"] as const,
  earnings: (days: number) => [...queryKeys.all, "earnings", days] as const,
  latestMacro: () => [...queryKeys.all, "macro", "latest"] as const,
};

/** Don't retry 4xx; retry network/5xx up to twice. */
const retry = (count: number, err: unknown) =>
  !(err instanceof ApiError && err.status >= 400 && err.status < 500) && count < 2;

export const useApiHealthQuery = () =>
  useQuery({
    queryKey: queryKeys.health(),
    queryFn: ({ signal }) => api.getHealth({ signal }),
    staleTime: 30_000,
    refetchInterval: MIN,
    retry: 1,
  });

export const usePortfolioQuery = () =>
  useQuery({
    queryKey: queryKeys.portfolio(),
    queryFn: ({ signal }) => api.getPortfolio({ signal }),
    staleTime: MIN,
    refetchInterval: 5 * MIN,
    retry,
  });

export const usePositionsQuery = () =>
  useQuery({
    queryKey: queryKeys.positions(),
    queryFn: ({ signal }) => api.getPositions({ signal }),
    staleTime: MIN,
    refetchInterval: 5 * MIN,
    retry,
  });

export const useHistoryQuery = (days = 365) =>
  useQuery({
    queryKey: queryKeys.history(days),
    queryFn: ({ signal }) => api.getHistory(days, { signal }),
    staleTime: 15 * MIN,
    retry,
  });

export const usePositionHistoryQuery = (ticker: string | null | undefined) => {
  const t = ticker?.trim() ?? "";
  return useQuery({
    queryKey: queryKeys.positionHistory(t),
    queryFn: ({ signal }) => api.getPositionHistory(t, { signal }),
    enabled: t.length > 0,
    staleTime: 15 * MIN,
    retry,
  });
};

export const useMonthlyReturnsQuery = () =>
  useQuery({
    queryKey: queryKeys.monthlyReturns(),
    queryFn: ({ signal }) => api.getMonthlyReturns({ signal }),
    staleTime: 60 * MIN,
    retry,
  });

export const useAnalyticsQuery = () =>
  useQuery({
    queryKey: queryKeys.analytics(),
    queryFn: ({ signal }) => api.getAnalytics({ signal }),
    staleTime: 15 * MIN,
    retry,
  });

export const useLatestReportQuery = () =>
  useQuery({
    queryKey: queryKeys.latestReport(),
    queryFn: ({ signal }) => api.getLatestReport({ signal }),
    staleTime: 30 * MIN,
    retry,
  });

export const useNewsQuery = () =>
  useQuery({
    queryKey: queryKeys.news(),
    queryFn: ({ signal }) => api.getNews({ signal }),
    staleTime: 10 * MIN,
    refetchInterval: 15 * MIN,
    retry,
  });

export const useEarningsQuery = (days = 30) =>
  useQuery({
    queryKey: queryKeys.earnings(days),
    queryFn: ({ signal }) => api.getEarnings(days, { signal }),
    staleTime: 60 * MIN,
    retry,
  });

export const useLatestMacroQuery = () =>
  useQuery({
    queryKey: queryKeys.latestMacro(),
    queryFn: ({ signal }) => api.getLatestMacro({ signal }),
    staleTime: 60 * MIN,
    retry,
  });

export type ApiConnectionState = "checking" | "online" | "degraded" | "offline";

/** Lightweight backend connection status derived from /api/health. */
export function useApiConnection() {
  const q = useApiHealthQuery();
  let state: ApiConnectionState = "checking";
  if (q.isError) state = "offline";
  else if (q.data) state = q.data.status === "ok" ? "online" : "degraded";
  return { state, health: q.data, error: q.error, refetch: q.refetch, isFetching: q.isFetching };
}

/** Invalidate all backend queries, or a subset of key groups. */
export function useDashboardRefresh() {
  const qc = useQueryClient();
  return useCallback(
    (keys?: ReadonlyArray<readonly unknown[]>) =>
      keys
        ? Promise.all(keys.map((queryKey) => qc.invalidateQueries({ queryKey })))
        : qc.invalidateQueries({ queryKey: queryKeys.all }),
    [qc],
  );
}
