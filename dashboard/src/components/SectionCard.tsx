import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type SectionCardProps = {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  className?: string;
  children?: ReactNode;
};

export function SectionCard({ title, subtitle, actions, className, children }: SectionCardProps) {
  return (
    <section className={cn("rounded-lg border border-border bg-card shadow-subtle", className)}>
      {(title || actions) && (
        <header className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border px-4 py-3">
          <div className="min-w-0">
            {title && (
              <h3 className="truncate font-mono text-xs font-medium uppercase tracking-widest text-muted-foreground">
                {title}
              </h3>
            )}
            {subtitle && <p className="mt-0.5 truncate text-xs text-muted-foreground">{subtitle}</p>}
          </div>
          {actions && <div className="shrink-0">{actions}</div>}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}
