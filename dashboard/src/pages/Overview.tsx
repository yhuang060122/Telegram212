import { RefreshCw } from "lucide-react";
import { PageContainer } from "@/components/PageContainer";
import { MetricCard } from "@/components/MetricCard";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { EquityCurveCard } from "@/components/overview/EquityCurveCard";
import {
  AiSummaryCard, DataSourcesCard, RiskSnapshotCard, SectorAllocationCard, TopHoldingsCard,
} from "@/components/overview/OverviewPanels";
import { overviewSource } from "@/lib/overview-source";
import { formatDateTime, formatKpi } from "@/lib/format";

export default function OverviewPage() {
  const data = overviewSource.getOverview();

  return (
    <PageContainer
      title="Overview"
      description="Portfolio snapshot: value, performance, risk and AI insight at a glance."
      actions={
        <div className="flex flex-wrap items-center justify-end gap-2">
          {overviewSource.isDemo && <StatusBadge status="warning">Demo data</StatusBadge>}
          <span className="hidden font-mono text-xs text-muted-foreground sm:inline">
            Updated <time dateTime={data.lastUpdated}>{formatDateTime(data.lastUpdated)}</time>
          </span>
          <Button variant="outline" size="sm" disabled className="h-7 gap-1.5 text-xs" aria-label="Refresh (unavailable in demo)" title="Not live — demo data">
            <RefreshCw className="h-3.5 w-3.5" aria-hidden /> Refresh
          </Button>
        </div>
      }
    >
      <p className="font-mono text-xs text-muted-foreground sm:hidden">
        Updated {formatDateTime(data.lastUpdated)}
      </p>

      <section aria-label="Key metrics" className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">
        {data.kpis.map((k, i) => (
          <MetricCard
            key={k.id}
            label={k.label}
            value={formatKpi(k.value, k.format)}
            hint={k.hint}
            tone={k.tone}
            className={i === 0 ? "col-span-2 md:col-span-1" : ""}
          />
        ))}
      </section>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <EquityCurveCard curve={data.equityCurve} />
        <RiskSnapshotCard risk={data.risk} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <SectorAllocationCard sectors={data.sectors} />
        <TopHoldingsCard holdings={data.topHoldings} />
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <AiSummaryCard ai={data.ai} />
        <DataSourcesCard sources={data.sources} />
      </div>
    </PageContainer>
  );
}
