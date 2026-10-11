
import { useQuery } from "@tanstack/react-query";

import { ApiError, dashboardApi } from "@/services/api";
import { mapOverviewData } from "./overview.mapper";

export const overviewKeys = {
  all: ["overview"] as const,
  portfolio: ["overview", "portfolio"] as const,
  analytics: ["overview", "analytics"] as const,
  history: (days: number) => ["overview", "history", days] as const,
  positions: ["overview", "positions"] as const,
  report: ["overview", "latest-report"] as const,
};

export function usePortfolioQuery() {
  return useQuery({
    queryKey: overviewKeys.portfolio,
    queryFn: dashboardApi.getPortfolio,
  });
}

export function useAnalyticsQuery() {
  return useQuery({
    queryKey: overviewKeys.analytics,
    queryFn: dashboardApi.getAnalytics,
  });
}

export function useHistoryQuery(days = 30) {
  return useQuery({
    queryKey: overviewKeys.history(days),
    queryFn: () => dashboardApi.getHistory(days),
  });
}

export function usePositionsQuery() {
  return useQuery({
    queryKey: overviewKeys.positions,
    queryFn: dashboardApi.getPositions,
  });
}

export function useLatestReportQuery() {
  return useQuery({
    queryKey: overviewKeys.report,
    queryFn: async () => {
      try {
        const response = await dashboardApi.getLatestReport();
        return response.report;
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) {
          return null;
        }
        throw error;
      }
    },
  });
}

export function useOverviewData(days = 30) {
  const portfolio = usePortfolioQuery();
  const analytics = useAnalyticsQuery();
  const history = useHistoryQuery(days);
  const positions = usePositionsQuery();
  const report = useLatestReportQuery();

  const isLoading =
    portfolio.isPending ||
    analytics.isPending ||
    history.isPending ||
    positions.isPending ||
    report.isPending;

  const error =
    portfolio.error ??
    analytics.error ??
    history.error ??
    positions.error ??
    report.error;

  const data =
    !isLoading &&
    !error &&
    portfolio.data &&
    analytics.data &&
    history.data &&
    positions.data
      ? mapOverviewData({
          portfolio: portfolio.data,
          analytics: analytics.data,
          history: history.data,
          positions: positions.data,
          report: report.data ?? null,
        })
      : undefined;

  return {
    data,
    isLoading,
    error,
    refetch: async () => {
      await Promise.all([
        portfolio.refetch(),
        analytics.refetch(),
        history.refetch(),
        positions.refetch(),
        report.refetch(),
      ]);
    },
  };
}
