import { useState } from "react";
import { Menu, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { SidebarNav } from "./Sidebar";

export function Header() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-20 grid h-[var(--header-height)] grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border bg-background/90 px-4 backdrop-blur md:px-6">
      <div className="flex min-w-0 items-center gap-2">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="shrink-0 md:hidden" aria-label="Open navigation">
              <Menu className="h-4 w-4" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[var(--sidebar-width)] border-sidebar-border bg-sidebar p-0">
            <SheetTitle className="sr-only">Navigation</SheetTitle>
            <SidebarNav onNavigate={() => setOpen(false)} />
          </SheetContent>
        </Sheet>
        <h1 className="truncate text-sm font-semibold tracking-tight">Trading212 AI Analyst</h1>
      </div>

      <div className="flex shrink-0 items-center gap-2 font-mono text-xs">
        <div className="hidden items-center gap-1.5 rounded-md border border-border px-2 py-1 sm:flex">
          <span className="text-muted-foreground">CCY</span>
          <span className="text-foreground">EUR</span>
        </div>
        <div className="flex items-center gap-1.5 rounded-md border border-border px-2 py-1">
          <span className="text-muted-foreground">UPD</span>
          <span className="tabular-nums text-foreground">--:--</span>
        </div>
        <Button variant="outline" size="sm" disabled className="h-7 gap-1.5 rounded-md text-xs">
          <RefreshCw className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Refresh</span>
        </Button>
      </div>
    </header>
  );
}
