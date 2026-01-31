CREATE TABLE IF NOT EXISTS ticks_clean (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  price DOUBLE PRECISION NOT NULL,
  size DOUBLE PRECISION NOT NULL,
  source TEXT NOT NULL,
  kind TEXT NOT NULL,
  zscore DOUBLE PRECISION,
  is_anomaly BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_ticks_clean_symbol_ts ON ticks_clean(symbol, ts DESC);

CREATE TABLE IF NOT EXISTS news_sentiment (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  headline TEXT NOT NULL,
  source TEXT NOT NULL,
  sentiment DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_news_symbol_ts ON news_sentiment(symbol, ts DESC);
