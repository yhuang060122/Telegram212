import { createFileRoute } from "@tanstack/react-router";

import AiReportPage from "@/pages/AiReport";

export const Route = createFileRoute("/ai-report")({
  head: () => ({
    meta: [
      { title: "AI Report — Trading212 AI Analyst" },
      { name: "description", content: "AI-generated portfolio report." },
      { property: "og:title", content: "AI Report — Trading212 AI Analyst" },
      { property: "og:description", content: "AI-generated portfolio report." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: AiReportPage,
});
