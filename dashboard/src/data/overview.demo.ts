/**
 * DEMO / SAMPLE DATA ONLY — not real portfolio data.
 * All values are precomputed here; components only display them.
 */
import type { EquityPoint, OverviewData } from "@/types/overview";

// Deterministic sample series so the chart is stable between renders.
function sampleSeries(days: number, end: number, seed: number): EquityPoint[] {
  const points: EquityPoint[] = [];
  const endDate = new Date("2026-09-25T00:00:00Z");
  let s = seed;
  const rand = () => ((s = (s * 9301 + 49297) % 233280) / 233280);
  let v = end * 0.86;
  const drift = (end - v) / days;
  for (let i = days; i >= 0; i--) {
    const d = new Date(endDate);
    d.setUTCDate(endDate.getUTCDate() - i);
    v += drift + (rand() - 0.5) * end * 0.012;
    points.push({ date: d.toISOString().slice(0, 10), value: v });
  }
  // Bend the random walk so it lands exactly on today's value.
  const gap = end - points[points.length - 1]!.value;
  return points.map((p, i) => ({ ...p, value: Math.round((p.value + (gap * i) / days) * 100) / 100 }));
}

const year = sampleSeries(365, 48_732.4, 7);

export const overviewDemo: OverviewData = {
  currency: "EUR",
  lastUpdated: "2026-09-25T16:35:00Z",
  kpis: [
    { id: "value", label: "Portfolio Value", value: 48732.4, format: "currency", tone: "neutral", hint: "Invested + cash" },
    { id: "pl", label: "Today P/L", value: 312.85, format: "signedCurrency", tone: "positive", hint: "vs. previous close" },
    { id: "pct", label: "Today %", value: 0.65, format: "signedPercent", tone: "positive", hint: "Daily change" },
    { id: "ret", label: "Total Return", value: 14.2, format: "signedPercent", tone: "positive", hint: "Since first deposit" },
    { id: "cash", label: "Cash Ratio", value: 6.8, format: "percent", tone: "neutral", hint: "€3,314 uninvested" },
  ],
  equityCurve: {
    "1M": year.slice(-31),
    "3M": year.slice(-92),
    "1Y": year,
  },
  risk: {
    metrics: [
      { label: "Max Drawdown", value: "−11.4%", tone: "negative", hint: "Peak to trough, 1Y" },
      { label: "Volatility", value: "16.9%", tone: "neutral", hint: "Annualised, 1Y" },
      { label: "Sharpe", value: "1.12", tone: "positive", hint: "Risk-free: sample rate" },
      { label: "HHI", value: "0.142", tone: "neutral", hint: "Position concentration" },
    ],
    concentrationLevel: "Moderate",
    note: "Top 5 positions make up 52% of the portfolio.",
  },
  sectors: [
    { sector: "Technology", weight: 34.5 },
    { sector: "Healthcare", weight: 14.2 },
    { sector: "Financials", weight: 12.8 },
    { sector: "Consumer", weight: 11.1 },
    { sector: "Industrials", weight: 9.6 },
    { sector: "Energy", weight: 6.0 },
    { sector: "Other", weight: 5.0 },
    { sector: "Cash", weight: 6.8 },
  ],
  topHoldings: [
    { ticker: "AAPL", name: "Apple Inc.", weight: 13.4, value: 6530.14, returnPct: 22.8 },
    { ticker: "MSFT", name: "Microsoft Corp.", weight: 11.9, value: 5799.16, returnPct: 18.3 },
    { ticker: "ASML", name: "ASML Holding", weight: 9.7, value: 4727.04, returnPct: -4.6 },
    { ticker: "NOVO", name: "Novo Nordisk", weight: 8.6, value: 4190.99, returnPct: -9.1 },
    { ticker: "VWCE", name: "Vanguard FTSE All-World", weight: 8.4, value: 4093.52, returnPct: 11.7 },
  ],
  ai: {
    sentiment: "Neutral",
    headline: "Growth-tilted portfolio with rising tech concentration",
    summary:
      "Technology now accounts for roughly a third of holdings, driven by recent gains in AAPL and MSFT. Healthcare exposure lags after NOVO's pullback. Consider whether current concentration still matches your risk tolerance.",
    generatedAt: "2026-09-25T07:00:00Z",
    isSample: true,
  },
  sources: [
    { name: "Trading212", purpose: "Positions & cash", status: "Healthy", detail: "Sample sync" },
    { name: "Finnhub", purpose: "Prices & news", status: "Partial", detail: "2 symbols missing" },
    { name: "FRED", purpose: "Macro & risk-free rate", status: "Healthy", detail: "Sample sync" },
    { name: "Gemini", purpose: "AI analysis", status: "Failed", detail: "Last run errored" },
  ],
};
