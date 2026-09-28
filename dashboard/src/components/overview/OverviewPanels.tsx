import { Link } from "@tanstack/react-router";
import { ArrowUpRight, Sparkles } from "lucide-react";
import { SectionCard } from "@/components/SectionCard";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { formatCurrency, formatDateTime, formatPercent, formatSignedPercent } from "@/lib/format";
import { cn } from "@/lib/utils";
import type {
  AiSummary, DataSource, Holding, RiskLevel, RiskSnapshot, Sentiment, SectorWeight, SourceHealth, Tone,
} from "@/types/overview";

const toneText: Record<Tone, string> = {
  positive: "text-positive",
  negative: "text-negative",
  neutral: "text-foreground",
};
const riskStatus: Record<RiskLevel, "positive" | "warning" | "negative"> = { Low: "positive", Moderate: "warning", High: "negative" };
const sentimentStatus: Record<Sentiment, "positive" | "neutral" | "negative"> = { Bullish: "positive", Neutral: "neutral", Bearish: "negative" };
const healthStatus: Record<SourceHealth, "positive" | "warning" | "negative"> = { Healthy: "positive", Partial: "warning", Failed: "negative" };

function CardLink({ to, label }: { to: "/allocation" | "/holdings" | "/ai-report" | "/risk"; label: string }) {
  return (
    <Link
      to={to}
      className="inline-flex items-center gap-1 rounded-sm font-mono text-[11px] uppercase tracking-widest text-muted-foreground hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      {label} <ArrowUpRight className="h-3 w-3" aria-hidden />
    </Link>
  );
}

export function RiskSnapshotCard({ risk }: { risk: RiskSnapshot }) {
  return (
    <SectionCard title="Risk snapshot" actions={<CardLink to="/risk" label="Risk" />} className="min-w-0">
      <div className="flex items-center justify-between gap-2 rounded-md border border-border bg-surface-raised px-3 py-2.5">
        <span className="text-xs text-muted-foreground">Concentration risk</span>
        <StatusBadge status={riskStatus[risk.concentrationLevel]}>{risk.concentrationLevel}</StatusBadge>
      </div>
      <dl className="mt-3 divide-y divide-border">
        {risk.metrics.map((m) => (
          <div key={m.label} className="flex items-baseline justify-between gap-3 py-2.5">
            <div className="min-w-0">
              <dt className="text-sm">{m.label}</dt>
              <p className="truncate text-[11px] text-muted-foreground">{m.hint}</p>
            </div>
            <dd className={cn("shrink-0 font-mono text-sm font-medium tabular-nums", toneText[m.tone])}>{m.value}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-3 text-xs text-muted-foreground">{risk.note}</p>
    </SectionCard>
  );
}

export function SectorAllocationCard({ sectors }: { sectors: SectorWeight[] }) {
  if (!sectors.length) return <SectionCard title="Sector allocation"><EmptyState title="No sector data" /></SectionCard>;
  const max = Math.max(...sectors.map((s) => s.weight));
  return (
    <SectionCard title="Sector allocation" actions={<CardLink to="/allocation" label="Allocation" />} className="min-w-0">
      <ul className="space-y-2.5">
        {sectors.map((s) => (
          <li key={s.sector} className="grid grid-cols-[6.5rem_minmax(0,1fr)_3.5rem] items-center gap-3">
            <span className="truncate text-xs">{s.sector}</span>
            <div className="h-2 overflow-hidden rounded-full bg-muted" aria-hidden>
              <div className="h-full rounded-full bg-primary/80" style={{ width: `${(s.weight / max) * 100}%` }} />
            </div>
            <span className="text-right font-mono text-xs tabular-nums text-muted-foreground">{formatPercent(s.weight)}</span>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}

export function TopHoldingsCard({ holdings }: { holdings: Holding[] }) {
  return (
    <SectionCard title="Top 5 holdings" actions={<CardLink to="/holdings" label="Holdings" />} className="min-w-0">
      {holdings.length === 0 ? (
        <EmptyState title="No holdings yet" />
      ) : (
        <table className="w-full text-sm">
          <caption className="sr-only">Largest five positions by weight</caption>
          <thead>
            <tr className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              <th scope="col" className="pb-2 text-left font-normal">Ticker</th>
              <th scope="col" className="pb-2 text-right font-normal">Weight</th>
              <th scope="col" className="hidden pb-2 text-right font-normal sm:table-cell">Value</th>
              <th scope="col" className="pb-2 text-right font-normal">Return</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {holdings.map((h) => (
              <tr key={h.ticker}>
                <td className="max-w-0 py-2.5 pr-2">
                  <div className="font-mono text-sm font-semibold">{h.ticker}</div>
                  <div className="truncate text-[11px] text-muted-foreground">{h.name}</div>
                </td>
                <td className="py-2.5 text-right font-mono tabular-nums">{formatPercent(h.weight)}</td>
                <td className="hidden py-2.5 text-right font-mono tabular-nums sm:table-cell">{formatCurrency(h.value)}</td>
                <td className={cn("py-2.5 text-right font-mono tabular-nums", h.returnPct >= 0 ? "text-positive" : "text-negative")}>
                  {formatSignedPercent(h.returnPct)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </SectionCard>
  );
}

export function AiSummaryCard({ ai }: { ai: AiSummary }) {
  return (
    <SectionCard
      title="Latest AI summary"
      actions={<CardLink to="/ai-report" label="Full report" />}
      className="min-w-0"
    >
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge status={sentimentStatus[ai.sentiment]}>{ai.sentiment}</StatusBadge>
        {ai.isSample && <StatusBadge status="info" dot={false}>Sample analysis</StatusBadge>}
      </div>
      <h4 className="mt-3 flex items-start gap-2 text-base font-semibold leading-snug">
        <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden />
        {ai.headline}
      </h4>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{ai.summary}</p>
      <p className="mt-4 font-mono text-[11px] text-muted-foreground">
        Generated <time dateTime={ai.generatedAt}>{formatDateTime(ai.generatedAt)}</time> · demo content, not advice
      </p>
    </SectionCard>
  );
}

export function DataSourcesCard({ sources }: { sources: DataSource[] }) {
  return (
    <SectionCard title="Data sources" subtitle="Sample status — no live connections" className="min-w-0">
      <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
        {sources.map((s) => (
          <li key={s.name} className="flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2.5">
            <div className="min-w-0">
              <div className="text-sm font-medium">{s.name}</div>
              <div className="truncate text-[11px] text-muted-foreground">{s.purpose} · {s.detail}</div>
            </div>
            <StatusBadge status={healthStatus[s.status]} className="shrink-0">{s.status}</StatusBadge>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}
