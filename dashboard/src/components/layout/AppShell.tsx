import type { ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen w-full bg-background">
      <Sidebar />
      <div className="flex min-h-screen flex-col md:pl-[var(--sidebar-width)]">
        <Header />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
