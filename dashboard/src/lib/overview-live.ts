import type {
  AnalyticsResponse,
  HistoryResponse,
  LatestReportResponse,
  PortfolioResponse,
  PositionsResponse,
} from "@/types/api";
import type {
  DataSource,
  EquityPoint,
  EquityRange,
  Holding,
  OverviewData,
  RiskLevel,
  Sentiment,
  SourceHealth,
  Tone,
} from "@/types/overview";

const numberOr = (value: number | null | undefined, fallback = 0) =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;

const dateAtUtcMidnight = (date?: string | null) =>
  date ? `${date.slice(0, 10)}T00:00:00Z` : new Date().toISOString();

const toneFor = (value: number): Tone =>
  value > 0 ? "positive" : value < 0 ? "negative" : "neutral";

const sentimentFor = (value?: string | null): Sentiment => {
  const normalized = value?.toLowerCase();
  if (normalized === "bullish") return "Bullish";
  if (normalized === "bearish") return "Bearish";
  return "Neutral";
};

const riskLevelFor = (value?: string | null): RiskLevel => {
  const normalized = value?.toLowerCase();
  if (normalized === "high") return "High";
  if (normalized === "moderate" || normalized === "medium") return "Moderate";
  return "Low";
};

function sourceHealth(value?: string | null): SourceHealth {
  const normalized = value?.toLowerCase();

  if (
    normalized === "connected" ||
    normalized === "ok" ||
    normalized === "healthy" ||
    normalized === "success"
  ) {
    return "Healthy";
  }

  if (normalized === "partial" || normalized === "degraded" || normalized === "warning") {
    return "Partial";
  }

  if (normalized === "failed" || normalized === "error" || normalized === "disconnected") {
    return "Failed";
  }

  return "Partial";
}

function mapDataSources(
  report: LatestReportResponse | undefined,
  healthStatus?: string,
): DataSource[] {
  const statuses = report?.report?.data_status;

  return [
    {
      name: "Trading212",
      purpose: "Portfolio & positions",
      status: statuses?.trading212
        ? sourceHealth(statuses.trading212)
        : healthStatus === "ok"
          ? "Healthy"
          : "Partial",
      detail: statuses?.trading212 ?? "Backend reachable; source status unavailable",
    },
    {
      name: "Finnhub",
      purpose: "Market data",
      status: sourceHealth(statuses?.finnhub),
      detail: statuses?.finnhub ?? "Source status unavailable",
    },
    {
      name: "FRED",
      purpose: "Macro indicators",
      status: sourceHealth(statuses?.fred),
      detail: statuses?.fred ?? "Source status unavailable",
    },
    {
      name: "Gemini",
      purpose: "AI analysis",
      status: sourceHealth(statuses?.gemini),
      detail: statuses?.gemini ?? "Source status unavailable",
    },
  ];
}

export function buildLiveOverview(input: {
  portfolio: PortfolioResponse;
  positions: PositionsResponse;
  history: HistoryResponse;
  analytics: AnalyticsResponse;
  report?: LatestReportResponse;
  healthStatus?: string;
}): OverviewData {
  const { portfolio, positions, history, analytics, report, healthStatus } = input;
  const performance = analytics.performance;
  const risk = analytics.risk;
  const concentration = risk?.concentration;

  const totalValue = numberOr(portfolio.total_value);
  const unrealizedPnl = numberOr(portfolio.unrealized_pnl);
  const cashRatio = numberOr(portfolio.cash_ratio);
  const monthlyReturn = numberOr(performance?.monthly_return);
  const twr = numberOr(performance?.twr);

  const points: EquityPoint[] = [...(history.items ?? [])]
    .filter((item) => typeof item.total_value === "number")
    .sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date))
    .map((item) => ({
      date: item.snapshot_date,
      value: numberOr(item.total_value),
    }));

  const cutoff = (days: number) => {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - days);
    return date.toISOString().slice(0, 10);
  };

  const rangePoints = (range: EquityRange) => {
    const days = range === "1M" ? 31 : range === "3M" ? 92 : 365;
    const selected = points.filter((point) => point.date >= cutoff(days));
    // If the API has only older snapshots, keep the available history visible.
    return selected.length ? selected : points;
  };

  const sectorItems = (analytics.sector_allocation ?? [])
    .filter((item) => item.name && typeof item.weight === "number")
    .map((item) => ({
      sector: item.name,
      weight: numberOr(item.weight),
    }))
    .sort((a, b) => b.weight - a.weight);

  const topHoldings: Holding[] = [...(positions.items ?? [])]
    .sort((a, b) => numberOr(b.market_value) - numberOr(a.market_value))
    .slice(0, 5)
    .map((position) => ({
      ticker: position.ticker,
      name: position.name || position.ticker,
      weight: numberOr(position.weight),
      value: numberOr(position.market_value),
      returnPct: numberOr(position.return_pct),
    }));

  const top5 = numberOr(concentration?.top5);
  const concentrationLevel = riskLevelFor(concentration?.risk_level);

  const summary = report?.report?.portfolio_rating;
  const generatedAt = dateAtUtcMidnight(portfolio.snapshot_date);

  const sources = mapDataSources(report, healthStatus);

  return {
    currency: "EUR",
    lastUpdated: generatedAt,
    kpis: [
      {
        id: "value",
        label: "Portfolio Value",
        value: totalValue,
        format: "currency",
        tone: "neutral",
        hint: `Invested ${numberOr(portfolio.invested).toLocaleString("en-IE", {
          style: "currency",
          currency: "EUR",
          maximumFractionDigits: 0,
        })} + cash`,
      },
      {
        id: "unrealized-pnl",
        label: "Unrealized P/L",
        value: unrealizedPnl,
        format: "signedCurrency",
        tone: toneFor(unrealizedPnl),
        hint: "Open positions",
      },
      {
        id: "cash-ratio",
        label: "Cash Ratio",
        value: cashRatio,
        format: "percent",
        tone: "neutral",
        hint: `Cash ${numberOr(portfolio.cash).toLocaleString("en-IE", {
          style: "currency",
          currency: "EUR",
          maximumFractionDigits: 0,
        })}`,
      },
      {
        id: "monthly-return",
        label: "Monthly Return",
        value: monthlyReturn,
        format: "signedPercent",
        tone: toneFor(monthlyReturn),
        hint: "Backend analytics",
      },
      {
        id: "twr",
        label: "Time-Weighted Return",
        value: twr,
        format: "signedPercent",
        tone: toneFor(twr),
        hint: "TWR · backend analytics",
      },
    ],
    equityCurve: {
      "1M": rangePoints("1M"),
      "3M": rangePoints("3M"),
      "1Y": rangePoints("1Y"),
    },
    risk: {
      metrics: [
        {
          label: "Max Drawdown",
          value: `${numberOr(risk?.max_drawdown).toFixed(2)}%`,
          tone: toneFor(numberOr(risk?.max_drawdown)),
          hint: "Maximum observed drawdown",
        },
        {
          label: "Volatility",
          value: `${numberOr(risk?.volatility).toFixed(2)}%`,
          tone: "neutral",
          hint: "Backend risk metric",
        },
        {
          label: "Sharpe Ratio",
          value: numberOr(risk?.sharpe).toFixed(2),
          tone: numberOr(risk?.sharpe) >= 1 ? "positive" : "neutral",
          hint: "Risk-adjusted return",
        },
        {
          label: "Top 5 Weight",
          value: `${top5.toFixed(2)}%`,
          tone: top5 >= 50 ? "negative" : top5 >= 35 ? "neutral" : "positive",
          hint: "Largest five positions",
        },
      ],
      concentrationLevel,
      note: `Top 1: ${numberOr(concentration?.top1).toFixed(2)}% · Top 3: ${numberOr(concentration?.top3).toFixed(2)}% · HHI: ${numberOr(concentration?.herfindahl).toFixed(4)}`,
    },
    sectors: sectorItems,
    topHoldings,
    ai: {
      sentiment: sentimentFor(summary?.overall_sentiment),
      headline: summary?.overall_sentiment
        ? `Portfolio outlook: ${summary.overall_sentiment}`
        : "AI report unavailable",
      summary:
        summary?.summary ??
        "No AI portfolio summary is available. Check the backend report pipeline and refresh the dashboard.",
      generatedAt,
    },
    sources,
  };
}
