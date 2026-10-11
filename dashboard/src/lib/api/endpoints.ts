/** One typed function per backend endpoint. Paths live only here. */
import { apiGet } from "./client";
import type {
  AnalyticsResponse,
  EarningsResponse,
  HealthResponse,
  HistoryResponse,
  LatestMacroResponse,
  LatestReportResponse,
  MonthlyReturnsResponse,
  NewsResponse,
  PortfolioResponse,
  PositionHistoryResponse,
  PositionsResponse,
} from "@/types/api";

type Opts = { signal?: AbortSignal };

export const API_PATHS = {
  health: "/api/health",
  portfolio: "/api/portfolio",
  positions: "/api/positions",
  history: "/api/history",
  positionHistory: (ticker: string) => `/api/positions/${encodeURIComponent(ticker)}/history`,
  monthlyReturns: "/api/monthly-returns",
  analytics: "/api/analytics",
  latestReport: "/api/reports/latest",
  news: "/api/news",
  earnings: "/api/earnings",
  latestMacro: "/api/macro/latest",
} as const;

export const api = {
  getHealth: (o: Opts = {}) => apiGet<HealthResponse>(API_PATHS.health, o),
  getPortfolio: (o: Opts = {}) => apiGet<PortfolioResponse>(API_PATHS.portfolio, o),
  getPositions: (o: Opts = {}) => apiGet<PositionsResponse>(API_PATHS.positions, o),
  getHistory: (days = 365, o: Opts = {}) =>
    apiGet<HistoryResponse>(API_PATHS.history, { ...o, params: { days } }),
  getPositionHistory: (ticker: string, o: Opts = {}) =>
    apiGet<PositionHistoryResponse>(API_PATHS.positionHistory(ticker), o),
  getMonthlyReturns: (o: Opts = {}) => apiGet<MonthlyReturnsResponse>(API_PATHS.monthlyReturns, o),
  getAnalytics: (o: Opts = {}) => apiGet<AnalyticsResponse>(API_PATHS.analytics, o),
  getLatestReport: (o: Opts = {}) => apiGet<LatestReportResponse>(API_PATHS.latestReport, o),
  getNews: (o: Opts = {}) => apiGet<NewsResponse>(API_PATHS.news, o),
  getEarnings: (days = 30, o: Opts = {}) =>
    apiGet<EarningsResponse>(API_PATHS.earnings, { ...o, params: { days } }),
  getLatestMacro: (o: Opts = {}) => apiGet<LatestMacroResponse>(API_PATHS.latestMacro, o),
};
