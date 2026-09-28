import {
  LayoutDashboard,
  TrendingUp,
  PieChart,
  Layers,
  ShieldAlert,
  Sparkles,
  Newspaper,
  type LucideIcon,
} from "lucide-react";

export type NavEntry = {
  label: string;
  to:
    | "/"
    | "/performance"
    | "/allocation"
    | "/holdings"
    | "/risk"
    | "/ai-report"
    | "/news";
  icon: LucideIcon;
};

export const NAV_ITEMS: NavEntry[] = [
  { label: "Overview", to: "/", icon: LayoutDashboard },
  { label: "Performance", to: "/performance", icon: TrendingUp },
  { label: "Allocation", to: "/allocation", icon: PieChart },
  { label: "Holdings", to: "/holdings", icon: Layers },
  { label: "Risk", to: "/risk", icon: ShieldAlert },
  { label: "AI Report", to: "/ai-report", icon: Sparkles },
  { label: "News", to: "/news", icon: Newspaper },
];
