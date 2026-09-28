import { createFileRoute } from "@tanstack/react-router";

import AllocationPage from "@/pages/Allocation";

export const Route = createFileRoute("/allocation")({
  head: () => ({
    meta: [
      { title: "Allocation — Trading212 AI Analyst" },
      { name: "description", content: "Portfolio allocation view." },
      { property: "og:title", content: "Allocation — Trading212 AI Analyst" },
      { property: "og:description", content: "Portfolio allocation view." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: AllocationPage,
});
