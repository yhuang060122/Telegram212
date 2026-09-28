import { createFileRoute } from "@tanstack/react-router";

import HoldingsPage from "@/pages/Holdings";

export const Route = createFileRoute("/holdings")({
  head: () => ({
    meta: [
      { title: "Holdings — Trading212 AI Analyst" },
      { name: "description", content: "Portfolio holdings view." },
      { property: "og:title", content: "Holdings — Trading212 AI Analyst" },
      { property: "og:description", content: "Portfolio holdings view." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: HoldingsPage,
});
