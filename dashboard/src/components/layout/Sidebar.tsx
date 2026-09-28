import { Activity } from "lucide-react";
import { NavItem } from "@/components/NavItem";
import { NAV_ITEMS } from "@/lib/navigation";

export function SidebarNav({ onNavigate }: { onNavigate?: (() => void) | undefined }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-[var(--header-height)] items-center gap-2 border-b border-sidebar-border px-4">
        <div className="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-primary text-primary-foreground">
          <Activity className="h-4 w-4" />
        </div>
        <span className="truncate font-mono text-xs font-semibold uppercase tracking-widest text-foreground">
          T212 Analyst
        </span>
      </div>
      <nav className="flex-1 space-y-0.5 p-2">
        <p className="px-3 pb-1 pt-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          Portfolio
        </p>
        {NAV_ITEMS.map((item) => (
          <NavItem key={item.to} {...item} onNavigate={onNavigate} />
        ))}
      </nav>
      <div className="border-t border-sidebar-border p-4 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
        v0.1 · Design system
      </div>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[var(--sidebar-width)] border-r border-sidebar-border bg-sidebar md:block">
      <SidebarNav />
    </aside>
  );
}
