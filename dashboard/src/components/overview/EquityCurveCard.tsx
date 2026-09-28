import { useState } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { SectionCard } from "@/components/SectionCard";
import { formatCurrency, formatCurrencyCompact, formatLongDate, formatShortDate } from "@/lib/format";
import type { EquityPoint, EquityRange } from "@/types/overview";
import { cn } from "@/lib/utils";

const RANGES: EquityRange[] = ["1M", "3M", "1Y"];

export function EquityCurveCard({ curve }: { curve: Record<EquityRange, EquityPoint[]> }) {
  const [range, setRange] = useState<EquityRange>("3M");
  const data = curve[range];

  return (
    <SectionCard
      title="Portfolio value"
      subtitle="Sample equity curve · EUR"
      className="min-w-0"
      actions={
        <div role="tablist" aria-label="Chart range" className="flex rounded-md border border-border p-0.5">
          {RANGES.map((r) => (
            <button
              key={r}
              role="tab"
              aria-selected={range === r}
              onClick={() => setRange(r)}
              className={cn(
                "rounded-sm px-2.5 py-1 font-mono text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                range === r ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground",
              )}
            >
              {r}
            </button>
          ))}
        </div>
      }
    >
      <div className="h-64 w-full sm:h-80" role="img" aria-label={`Portfolio value over ${range}`}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.28} />
                <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatShortDate}
              tick={{ fill: "var(--muted-foreground)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={false}
              tickLine={false}
              minTickGap={32}
            />
            <YAxis
              domain={["auto", "auto"]}
              tickFormatter={formatCurrencyCompact}
              tick={{ fill: "var(--muted-foreground)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={false}
              tickLine={false}
              width={60}
            />
            <Tooltip
              cursor={{ stroke: "var(--muted-foreground)", strokeDasharray: "3 3" }}
              content={({ active, payload }) => {
                const p = payload?.[0]?.payload as EquityPoint | undefined;
                if (!active || !p) return null;
                return (
                  <div className="rounded-md border border-border bg-popover px-3 py-2 font-mono text-xs">
                    <div className="text-muted-foreground">{formatLongDate(p.date)}</div>
                    <div className="mt-0.5 tabular-nums text-foreground">{formatCurrency(p.value)}</div>
                  </div>
                );
              }}
            />
            <Area type="monotone" dataKey="value" stroke="var(--chart-1)" strokeWidth={1.75} fill="url(#equityFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}
