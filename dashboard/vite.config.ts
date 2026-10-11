// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - TanStack devtools (dev-only, first), tanstackStart, viteReact, tailwindcss, tsConfigPaths,
//     nitro (build-only using cloudflare as a default target), VITE_* env injection, @ path alias,
//     React/TanStack dedupe, error logger plugins, and sandbox detection (port/host/strictPort).
// You can pass additional config via defineConfig({ vite: { ... }, etc... }) if needed.
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this
    server: { entry: "server" },
    // Emit a static SPA shell at the output root so GitHub Pages can serve it.
    spa: {
      enabled: true,
      prerender: { outputPath: "/index.html", crawlLinks: false },
    },
  },
  vite: {
    // Serve production assets from the GitHub Pages repo path.
    base: process.env["GITHUB_ACTIONS"] === "true" ? "/Telegram212/" : "/",
    // Pre-bundle the menu's slide-out panel with React so it never loads a second copy.
    optimizeDeps: { include: ["@radix-ui/react-dialog", "recharts", "lucide-react"] },
  },
});
