
import type {
  AnalyticsResponse,
  HistoryResponse,
  PortfolioResponse,
  PositionsResponse,
  Report,
} from "@/types/api";

export interface OverviewData {
  asOfDate: string;
  currency: string;

  kpis: {
    totalValue: number;
    currentValue: number;
    invested: number;
    cash: number;
    cashRatio: number;
    unrealizedPnl: number;
    realizedPnl: number;
  };

  performance: AnalyticsResponse["performance"];
  risk: AnalyticsResponse["risk"];

  history: HistoryResponse["items"];
  sectorAllocation: AnalyticsResponse["sector_allocation"];
  positionAllocation: AnalyticsResponse["position_allocation"];
  positions: PositionsResponse["items"];

  report: Report | null;
}

interface OverviewSources {
  portfolio: PortfolioResponse;
  analytics: AnalyticsResponse;
  history: HistoryResponse;
  positions: PositionsResponse;
  report: Report | null;
}

export function mapOverviewData(
  sources: OverviewSources,
): OverviewData {
  const {
    portfolio,
    analytics,
    history,
    positions,
    report,
  } = sources;

  return {
    asOfDate: portfolio.snapshot_date,
    currency: portfolio.currency,

    kpis: {
      totalValue: portfolio.total_value,
      currentValue: portfolio.current_value,
      invested: portfolio.invested,
      cash: portfolio.cash,
      cashRatio: portfolio.cash_ratio,
      unrealizedPnl: portfolio.unrealized_pnl,
      realizedPnl: portfolio.realized_pnl,
    },

    // 保留后端原始单位，不在 Mapper 中转换百分比。
    performance: analytics.performance,
    risk: analytics.risk,

    // 后端返回的历史顺序保持不变。
    history: history.items,
    sectorAllocation: analytics.sector_allocation,
    positionAllocation: analytics.position_allocation,
    positions: positions.items,
    report,
  };
}
