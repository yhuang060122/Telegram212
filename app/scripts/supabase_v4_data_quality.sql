alter table news
add constraint uq_news_identity
unique (ticker, published_at, url);

alter table earnings
add constraint uq_earnings_identity
unique (ticker, earnings_date, session);