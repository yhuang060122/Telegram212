create table if not exists cashflows (

    reference text primary key,

    datetime timestamptz not null,

    amount numeric not null,

    currency text not null,

    type text not null
);

create index if not exists idx_cashflows_datetime
on cashflows(datetime desc);