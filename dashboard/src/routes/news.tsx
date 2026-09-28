import { createFileRoute } from "@tanstack/react-router";

import NewsPage from "@/pages/News";

export const Route = createFileRoute("/news")({
  head: () => ({
    meta: [
      { title: "News — Trading212 AI Analyst" },
      { name: "description", content: "Market news relevant to your portfolio." },
      { property: "og:title", content: "News — Trading212 AI Analyst" },
      { property: "og:description", content: "Market news relevant to your portfolio." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: NewsPage,
});
