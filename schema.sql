CREATE TABLE IF NOT EXISTS users (
    telegram_id   BIGINT PRIMARY KEY,
    username      TEXT,
    favorite_team TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
