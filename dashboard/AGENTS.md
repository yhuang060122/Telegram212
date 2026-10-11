<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

## Architecture decisions

- Routing uses TanStack Router (`@tanstack/react-router`) instead of React Router — the platform stack is fixed on TanStack Start and doesn't support react-router-dom; route files live in `src/routes/`, page components live in `src/pages/`.
- Backend access goes only through the FastAPI client in `src/lib/api/` (typed endpoints + TanStack Query hooks in `src/hooks/queries/`) — the dashboard never talks to Supabase directly, so credentials stay server-side.
- Design tokens live in `src/styles/tokens.css` (raw oklch values, dark-first) and are mapped to Tailwind utilities in `src/styles/theme.css` — components use semantic utilities only, never raw colors.
- App chrome (`AppShell` = fixed Sidebar + Header, mobile Sheet nav) wraps `<Outlet />` in `__root.tsx`; nav entries are defined once in `src/lib/navigation.ts`.
- Page data goes through a source module (e.g. `src/lib/overview-source.ts`) backed by typed demo data in `src/data/` with types in `src/types/` — swap the source later for the real backend without touching components; components only format and display.
