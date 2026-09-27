import { createFileRoute } from "@tanstack/react-router";

import Home from "@/pages/Home";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Trading212 AI Analyst" },
      {
        name: "description",
        content: "AI analyst dashboard for your Trading212 portfolio.",
      },
      { property: "og:title", content: "Trading212 AI Analyst" },
      {
        property: "og:description",
        content: "AI analyst dashboard for your Trading212 portfolio.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Home,
});
