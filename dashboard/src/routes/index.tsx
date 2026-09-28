import { createFileRoute } from "@tanstack/react-router";

import OverviewPage from "@/pages/Overview";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Overview — Trading212 AI Analyst" },
      { name: "description", content: "Portfolio overview in your Trading212 AI Analyst dashboard." },
      { property: "og:title", content: "Overview — Trading212 AI Analyst" },
      { property: "og:description", content: "Portfolio overview in your Trading212 AI Analyst dashboard." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: OverviewPage,
});
