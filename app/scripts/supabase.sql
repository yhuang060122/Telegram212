-- ============================================================
-- Trading212 AI Database Schema
-- PostgreSQL / Supabase
-- ============================================================

create extension if not exists pgcrypto;

-- ------------------------------------------------------------
-- updated_at trigger
-- ------------------------------------------------------------

create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- ============================================================
-- SNAPSHOTS
-- ============================================================

create table if not exists snapshots (

    snapshot_date date primary key,

    total_value numeric(14,2) not null,
    cash numeric(14,2) not null,
    cash_ratio numeric(5,2) not null,

    invested numeric(14,2) not null,
    current_value numeric(14,2) not null,

    unrealized_pnl numeric(14,2) not null,
    realized_pnl numeric(14,2) not null,

    currency varchar(3) not null default 'EUR',

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create trigger trg_snapshots_updated
before update on snapshots
for each row
execute function update_updated_at_column();

-- ============================================================
-- POSITIONS
-- ============================================================

create table if not exists positions (

    snapshot_date date not null,

    ticker text not null,
    name text not null,

    quantity numeric(18,6) not null,

    avg_price numeric(14,4) not null,
    current_price numeric(14,4) not null,

    market_value numeric(14,2) not null,
    cost numeric(14,2) not null,

    pnl numeric(14,2) not null,
    return_pct numeric(8,2) not null,

    weight numeric(6,2) not null,

    sector text,
    fx_impact numeric(14,2),
    inst_currency varchar(3),

    created_at timestamptz default now(),
    updated_at timestamptz default now(),

    primary key (snapshot_date, ticker),

    constraint fk_positions_snapshot
        foreign key (snapshot_date)
        references snapshots(snapshot_date)
        on delete cascade
);

create trigger trg_positions_updated
before update on positions
for each row
execute function update_updated_at_column();

-- ============================================================
-- NEWS
-- ============================================================

create table if not exists news (

    id uuid primary key default gen_random_uuid(),

    snapshot_date date not null,

    ticker text not null,

    title text not null,

    source text,

    sentiment text
        check (sentiment in ('Bullish','Neutral','Bearish', 'Unknown')),

    url text,

    created_at timestamptz default now()
);

-- ============================================================
-- EARNINGS
-- ============================================================

create table if not exists earnings (

    id uuid primary key default gen_random_uuid(),

    snapshot_date date not null,

    ticker text not null,

    earnings_date date not null,

    session text
        check (session in ('BMO','AMC','During Market')),

    created_at timestamptz default now()
);

-- ============================================================
-- REPORTS
-- ============================================================

create table if not exists reports (

    snapshot_date date primary key,

    report jsonb not null,

    created_at timestamptz default now(),
    updated_at timestamptz default now(),

    constraint fk_reports_snapshot
        foreign key (snapshot_date)
        references snapshots(snapshot_date)
        on delete cascade
);

create trigger trg_reports_updated
before update on reports
for each row
execute function update_updated_at_column();

-- ============================================================
-- INDEXES
-- ============================================================

create index if not exists idx_positions_ticker
on positions(ticker);

create index if not exists idx_positions_weight
on positions(weight desc);

create index if not exists idx_news_date
on news(snapshot_date desc);

create index if not exists idx_news_ticker
on news(ticker);

create index if not exists idx_earnings_date
on earnings(earnings_date);

create index if not exists idx_reports_date
on reports(snapshot_date desc);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

alter table snapshots enable row level security;
alter table positions enable row level security;
alter table news enable row level security;
alter table earnings enable row level security;
alter table reports enable row level security;

-- Read-only for Dashboard (anon)

create policy "anon_read_snapshots"
on snapshots
for select
to anon
using (true);

create policy "anon_read_positions"
on positions
for select
to anon
using (true);

create policy "anon_read_news"
on news
for select
to anon
using (true);

create policy "anon_read_earnings"
on earnings
for select
to anon
using (true);

create policy "anon_read_reports"
on reports
for select
to anon
using (true);

-- authenticated users (optional)

create policy "auth_read_snapshots"
on snapshots
for select
to authenticated
using (true);

create policy "auth_read_positions"
on positions
for select
to authenticated
using (true);

create policy "auth_read_news"
on news
for select
to authenticated
using (true);

create policy "auth_read_reports"
on reports
for select
to authenticated
using (true);