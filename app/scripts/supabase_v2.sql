-- ============================================================
-- Trading212 AI Migration V1 -> V2
-- Replace UUID PK with Business Composite PK
-- ============================================================

begin;

-- ============================================================
-- NEWS
-- UUID -> (ticker, published_at, url)
-- ============================================================

-- New columns
alter table news
    add column if not exists published_at timestamptz;

alter table news
    add column if not exists summary text;

-- Migrate date -> timestamp
update news
set published_at = snapshot_date::timestamptz
where published_at is null;

-- Default sentiment
update news
set sentiment = 'Unknown'
where sentiment is null;

-- URL cannot be null for composite PK
update news
set url = concat('legacy://', ticker, '/', snapshot_date)
where url is null;

-- Remove duplicate rows before creating PK
delete from news n1
using news n2
where n1.ctid < n2.ctid
  and n1.ticker = n2.ticker
  and n1.published_at = n2.published_at
  and n1.url = n2.url;

-- Drop old PK + UUID
alter table news
    drop constraint if exists news_pkey;

alter table news
    drop column if exists id;

alter table news
    drop column if exists snapshot_date;

alter table news
    alter column published_at set not null;

alter table news
    alter column url set not null;

alter table news
    alter column source set not null;

alter table news
    alter column sentiment set not null;

alter table news
    add constraint news_pkey
        primary key (ticker, published_at, url);

alter table news
    drop constraint if exists news_sentiment_check;

alter table news
    add constraint news_sentiment_check
        check (sentiment in ('Bullish','Neutral','Bearish','Unknown'));

-- ============================================================
-- EARNINGS
-- UUID -> (ticker, earnings_date)
-- ============================================================

alter table earnings
    add column if not exists company text default '';

alter table earnings
    add column if not exists eps_estimate numeric(12,4);

alter table earnings
    add column if not exists revenue_estimate numeric(18,2);

update earnings
set company = ticker
where company = '';

update earnings
set session = 'UNKNOWN'
where session not in ('BMO','AMC','During Market','UNKNOWN')
   or session is null;

-- Remove duplicates
delete from earnings e1
using earnings e2
where e1.ctid < e2.ctid
  and e1.ticker = e2.ticker
  and e1.earnings_date = e2.earnings_date;

alter table earnings
    drop constraint if exists earnings_pkey;

alter table earnings
    drop column if exists id;

alter table earnings
    drop constraint if exists earnings_session_check;

alter table earnings
    alter column company set not null;

alter table earnings
    alter column session set not null;

alter table earnings
    add constraint earnings_session_check
        check (session in ('BMO','AMC','During Market','UNKNOWN'));

alter table earnings
    add constraint earnings_pkey
        primary key (ticker, earnings_date);

-- ============================================================
-- MACRO
-- ============================================================

create table if not exists macro (

    snapshot_date date primary key,

    fed_rate numeric(8,3),
    us10y numeric(8,3),
    dxy numeric(8,3),
    vix numeric(8,3),

    inflation numeric(8,3),
    unemployment numeric(8,3),

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create trigger trg_macro_updated
before update on macro
for each row
execute function update_updated_at_column();

-- ============================================================
-- REPORTS
-- ============================================================

alter table reports
    add column if not exists overall_sentiment text;

update reports
set overall_sentiment =
    report -> 'portfolio_rating' ->> 'overall_sentiment'
where overall_sentiment is null;

-- ============================================================
-- INDEXES
-- ============================================================

drop index if exists idx_news_date;

create index if not exists idx_news_published
on news(published_at desc);

create index if not exists idx_news_ticker
on news(ticker);

create index if not exists idx_earnings_snapshot
on earnings(snapshot_date desc);

create index if not exists idx_earnings_date
on earnings(earnings_date);

create index if not exists idx_macro_date
on macro(snapshot_date desc);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

alter table macro enable row level security;

commit;