import { createFileRoute } from "@tanstack/react-router";

import PerformancePage from "@/pages/Performance";

export const Route = createFileRoute("/performance")({
  head: () => ({
    meta: [
      { title: "Performance — Trading212 AI Analyst" },
      { name: "description", content: "Portfolio performance view." },
      { property: "og:title", content: "Performance — Trading212 AI Analyst" },
      { property: "og:description", content: "Portfolio performance view." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: PerformancePage,
});
