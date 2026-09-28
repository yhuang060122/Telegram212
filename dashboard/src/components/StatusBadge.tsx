import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type Status = "neutral" | "positive" | "negative" | "warning" | "info";

const styles: Record<Status, string> = {
  neutral: "border-border text-muted-foreground",
  positive: "border-positive/30 bg-positive/10 text-positive",
  negative: "border-negative/30 bg-negative/10 text-negative",
  warning: "border-warning/30 bg-warning/10 text-warning",
  info: "border-info/30 bg-info/10 text-info",
};

export function StatusBadge({
  status = "neutral",
  dot = true,
  children,
  className,
}: {
  status?: Status;
  dot?: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 font-mono text-[11px] uppercase tracking-wider",
        styles[status],
        className,
      )}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}
