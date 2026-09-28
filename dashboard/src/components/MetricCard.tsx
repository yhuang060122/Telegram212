import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type Tone = "neutral" | "positive" | "negative" | "warning";

type MetricCardProps = {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: Tone;
  icon?: ReactNode;
  className?: string;
};

const toneClass: Record<Tone, string> = {
  neutral: "text-muted-foreground",
  positive: "text-positive",
  negative: "text-negative",
  warning: "text-warning",
};

export function MetricCard({ label, value, hint, tone = "neutral", icon, className }: MetricCardProps) {
  return (
    <div className={cn("rounded-lg border border-border bg-card p-4 shadow-subtle", className)}>
      <div className="flex items-center justify-between gap-2">
        <span className="truncate font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
          {label}
        </span>
        {icon && <span className="shrink-0 text-muted-foreground">{icon}</span>}
      </div>
      <div className="mt-2 truncate font-mono text-2xl font-semibold tabular-nums">{value}</div>
      {hint && <div className={cn("mt-1 truncate font-mono text-xs", toneClass[tone])}>{hint}</div>}
    </div>
  );
}
