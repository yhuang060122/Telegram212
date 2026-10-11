/**
 * Wire contracts for the Python FastAPI backend.
 * The dashboard must not query Supabase directly.
 */

export type IsoDate = string;
export type IsoDateTime = string;

export interface HealthResponse {
  status: string;
  service?: string;
  version?: string | null;
  timestamp?: IsoDateTime | null;
  [key: string]: unknown;
}

export interface Position {
  ticker: string;
  name?: string | null;
  quantity?: number | null;
  avg_price?: number | null;
  current_price?: number | null;
  market_value?: number | null;
  cost?: number | null;
  pnl?: number | null;
  weight?: number | null;
  fx_impact?: number | null;
  currency?: string | null;
  sector?: string | null;
  return_pct?: number | null;
  [key: string]: unknown;
}

export interface PortfolioSnapshot {
  snapshot_date?: IsoDate | null;
  currency?: string | null;
  total_value?: number | null;
  current_value?: number | null;
  invested?: number | null;
  cash?: number | null;
  cash_ratio?: number | null;
  unrealized_pnl?: number | null;
  realized_pnl?: number | null;
  positions?: Position[];
  [key: string]: unknown;
}

export type PortfolioResponse = PortfolioSnapshot;

export interface PositionsResponse {
  count: number;
  items: Position[];
}

export interface HistoryItem {
  snapshot_date: IsoDate;
  total_value?: number | null;
  current_value?: number | null;
  invested?: number | null;
  cash?: number | null;
  cash_ratio?: number | null;
  unrealized_pnl?: number | null;
  realized_pnl?: number | null;
  currency?: string | null;
  [key: string]: unknown;
}

export interface HistoryResponse {
  days: number;
  count: number;
  items: HistoryItem[];
}

export interface PositionHistoryPoint {
  date?: IsoDate;
  snapshot_date?: IsoDate;
  price?: number | null;
  value?: number | null;
  quantity?: number | null;
  [key: string]: unknown;
}

export interface PositionHistoryResponse {
  ticker?: string;
  count?: number;
  items?: PositionHistoryPoint[];
  [key: string]: unknown;
}

export interface MonthlyReturn {
  year?: number | null;
  month?: number | null;
  period?: string | null;
  return_pct?: number | null;
  [key: string]: unknown;
}

export interface MonthlyReturnsResponse {
  count?: number;
  items?: MonthlyReturn[];
  [key: string]: unknown;
}

export interface AnalyticsPerformance {
  daily_return?: number | null;
  weekly_return?: number | null;
  monthly_return?: number | null;
  twr?: number | null;
  xirr?: number | null;
  total_return?: number | null;
}

export interface AnalyticsConcentration {
  top1?: number | null;
  top3?: number | null;
  top5?: number | null;
  herfindahl?: number | null;
  risk_level?: string | null;
}

export interface AnalyticsRisk {
  concentration?: AnalyticsConcentration;
  volatility?: number | null;
  sharpe?: number | null;
  drawdown?: number | null;
  max_drawdown?: number | null;
}

export interface AllocationItem {
  name: string;
  weight?: number | null;
  value?: number | null;
  ticker?: string;
}

export interface AnalyticsResponse {
  performance?: AnalyticsPerformance;
  risk?: AnalyticsRisk;
  sector_allocation?: AllocationItem[];
  position_allocation?: AllocationItem[];
  [key: string]: unknown;
}

export interface AiPositionRating {
  ticker: string;
  name?: string | null;
  rating?: string | null;
  rationale?: string | null;
}

export interface AiPortfolioRating {
  overall_sentiment?: string | null;
  summary?: string | null;
  cash_strategy?: string | null;
  macro_outlook?: string | null;
}

export interface DataStatus {
  trading212?: string | null;
  finnhub?: string | null;
  fred?: string | null;
  gemini?: string | null;
  [key: string]: unknown;
}

export interface AiReport {
  portfolio_rating?: AiPortfolioRating | null;
  positions_ratings?: AiPositionRating[];
  data_status?: DataStatus;
  [key: string]: unknown;
}

export interface LatestReportResponse {
  report: AiReport | null;
}

export interface NewsItem {
  id?: string | number | null;
  headline?: string | null;
  title?: string | null;
  summary?: string | null;
  url?: string | null;
  source?: string | null;
  ticker?: string | null;
  published_at?: IsoDateTime | null;
  sentiment?: string | null;
  [key: string]: unknown;
}

export interface NewsResponse {
  count?: number;
  items?: NewsItem[];
  [key: string]: unknown;
}

export interface EarningsEvent {
  ticker: string;
  date?: IsoDate | null;
  hour?: string | null;
  eps_estimate?: number | null;
  eps_actual?: number | null;
  revenue_estimate?: number | null;
  revenue_actual?: number | null;
  [key: string]: unknown;
}

export interface EarningsResponse {
  count?: number;
  items?: EarningsEvent[];
  [key: string]: unknown;
}

export interface MacroData {
  date?: IsoDate | null;
  fed_funds_rate?: number | null;
  cpi?: number | null;
  unemployment?: number | null;
  treasury_10y?: number | null;
  [key: string]: unknown;
}

export interface LatestMacroResponse {
  data?: MacroData | null;
  [key: string]: unknown;
}
