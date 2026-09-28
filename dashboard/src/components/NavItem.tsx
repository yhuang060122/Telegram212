import { Link } from "@tanstack/react-router";
import type { LucideIcon } from "lucide-react";

type NavItemProps = {
  to: string;
  label: string;
  icon: LucideIcon;
  onNavigate?: (() => void) | undefined;
};

export function NavItem({ to, label, icon: Icon, onNavigate }: NavItemProps) {
  return (
    <Link
      to={to}
      onClick={onNavigate}
      activeOptions={{ exact: to === "/" }}
      className="group relative flex h-9 items-center gap-3 rounded-md px-3 text-sm text-sidebar-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
      activeProps={{
        className:
          "bg-sidebar-accent text-sidebar-accent-foreground before:absolute before:left-0 before:top-2 before:bottom-2 before:w-0.5 before:rounded-full before:bg-sidebar-primary",
      }}
    >
      <Icon className="h-4 w-4 shrink-0 opacity-80 group-[.active]:text-sidebar-primary" />
      <span className="truncate">{label}</span>
    </Link>
  );
}
