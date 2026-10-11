
import type {
  AnalyticsResponse,
  HistoryResponse,
  LatestReportResponse,
  PortfolioResponse,
  PositionsResponse,
} from "@/types/api";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    let message = `API request failed: ${response.status}`;

    try {
      const body = await response.json();
      if (typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // 保留默认错误信息。
    }

    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

export const dashboardApi = {
  getPortfolio: () =>
    request<PortfolioResponse>("/api/portfolio"),

  getAnalytics: () =>
    request<AnalyticsResponse>("/api/analytics"),

  getHistory: (days = 30) =>
    request<HistoryResponse>(`/api/history?days=${days}`),

  getPositions: () =>
    request<PositionsResponse>("/api/positions"),

  getLatestReport: () =>
    request<LatestReportResponse>("/api/reports/latest"),
};
