export type Tone = "positive" | "negative" | "neutral";
export type RiskLevel = "Low" | "Moderate" | "High";
export type Sentiment = "Bullish" | "Neutral" | "Bearish";
export type SourceHealth = "Healthy" | "Partial" | "Failed";
export type EquityRange = "1M" | "3M" | "1Y";

export type Kpi = {
  id: string;
  label: string;
  value: number;
  format: "currency" | "percent" | "signedCurrency" | "signedPercent";
  tone: Tone;
  hint?: string;
};

export type EquityPoint = { date: string; value: number };

export type RiskMetric = { label: string; value: string; tone: Tone; hint: string };

export type RiskSnapshot = {
  metrics: RiskMetric[];
  concentrationLevel: RiskLevel;
  note: string;
};

export type SectorWeight = { sector: string; weight: number };

export type Holding = {
  ticker: string;
  name: string;
  weight: number;
  value: number;
  returnPct: number;
};

export type AiSummary = {
  sentiment: Sentiment;
  headline: string;
  summary: string;
  generatedAt: string;
  isSample: true;
};

export type DataSource = {
  name: "Trading212" | "Finnhub" | "FRED" | "Gemini";
  purpose: string;
  status: SourceHealth;
  detail: string;
};

export type OverviewData = {
  currency: "EUR";
  lastUpdated: string;
  kpis: Kpi[];
  equityCurve: Record<EquityRange, EquityPoint[]>;
  risk: RiskSnapshot;
  sectors: SectorWeight[];
  topHoldings: Holding[];
  ai: AiSummary;
  sources: DataSource[];
};
