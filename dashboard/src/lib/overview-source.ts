/**
 * Data-access boundary for the Overview page.
 * Today it returns local demo data; later swap the implementation for the
 * Python backend / Supabase without touching components.
 */
import { overviewDemo } from "@/data/overview.demo";
import type { OverviewData } from "@/types/overview";

export type OverviewSource = { isDemo: boolean; getOverview: () => OverviewData };

export const overviewSource: OverviewSource = {
  isDemo: true,
  getOverview: () => overviewDemo,
};
