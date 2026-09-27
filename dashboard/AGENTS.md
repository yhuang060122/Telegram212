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
- No backend code yet: the dashboard will later connect to an external Python backend and Supabase owned by the user — keep server logic and data fetching out until then.
