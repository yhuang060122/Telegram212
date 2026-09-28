import { createFileRoute } from "@tanstack/react-router";

import RiskPage from "@/pages/Risk";

export const Route = createFileRoute("/risk")({
  head: () => ({
    meta: [
      { title: "Risk — Trading212 AI Analyst" },
      { name: "description", content: "Portfolio risk view." },
      { property: "og:title", content: "Risk — Trading212 AI Analyst" },
      { property: "og:description", content: "Portfolio risk view." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: RiskPage,
});
