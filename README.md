# GoalZone

[![CI](https://github.com/Qahramon1412/goalzone/actions/workflows/ci.yml/badge.svg)](https://github.com/Qahramon1412/goalzone/actions/workflows/ci.yml)

An Uzbek-language Telegram bot for Premier League data. It is a learning project that I use to practice Python and a DevOps/DevSecOps workflow: containers, automated checks, and security scanning.

## Features

| Command | What it does |
|---|---|
| `/start` | Welcome message, saves the user |
| `/today` | Today's Premier League matches (Tashkent time) |
| `/table` | Current league table |
| `/fixtures` | Matches for the next 7 days |
| `/favorite <team>` | Saves a favorite team (name, short name, or 3-letter code such as `ARS`) |
| `/my` | Upcoming matches of your favorite team |

If the football API is down or the rate limit is hit, the bot replies with a clear message instead of crashing.

## Architecture

```mermaid
flowchart LR
    U[Telegram user] <--> T[Telegram Bot API]
    T <--> B[Bot container]
    B -->|HTTPS, 60 s cache| F[football-data.org]
    B <--> D[(PostgreSQL)]
    P[Prometheus] -->|scrapes /metrics| B
```

The bot, the database and Prometheus run as three containers in Docker Compose. The database port is not published to the host, only the bot can reach it over the internal network.

## Quick start (Docker Compose)

1. Get a free token from [football-data.org](https://www.football-data.org/client/register) and create a bot with [@BotFather](https://t.me/BotFather).
2. Create your settings file and fill in the values:

```bash
cp .env.example .env
```

3. Start everything:

```bash
docker compose up -d --build
docker compose logs -f bot
```

`DB_USER`, `DB_PASSWORD` and `DB_NAME` from `.env` are also used to create the PostgreSQL container. The `users` table is created from `schema.sql` the first time the database starts.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -v
ruff check . && ruff format --check .
```

Running the bot outside Docker needs a local PostgreSQL with the schema from `schema.sql` loaded.

## CI (GitHub Actions)

Every push and pull request runs three jobs:

- **test**: `ruff` lint and format check, then `pytest` (no network or secrets needed).
- **dependency-audit**: `pip-audit` on `requirements.txt`. It also runs every Monday, because new vulnerabilities appear after a release.
- **image-scan**: builds the Docker image and scans it with Trivy (HIGH and CRITICAL, fixable issues only).

## Operations

Everything below runs locally with Docker Compose.

```bash
docker compose up -d --build   # start (or rebuild and start)
docker compose ps              # status and health
docker compose logs -f bot     # follow bot logs
docker compose down            # stop, data is kept
```

Never run `docker compose down -v` unless you want to delete the database volume.

**Restart and health.** Containers use `restart: unless-stopped`, so they come back after a crash and after Docker or WSL restarts. They do not come back after a manual `docker stop` or `docker kill`. The bot container has a `HEALTHCHECK`: the bot calls Telegram `get_me()` every 60 seconds and touches `/tmp/heartbeat`, and the check fails if that file is older than 180 seconds. Compose only marks such a container `unhealthy`, it does not restart it.

**Logs.** Docker keeps at most 3 files of 10 MB per container.

**Backups.** `scripts/backup.sh` runs `pg_dump`, checks that the dump is complete, and keeps the 7 newest files in `~/backups/goalzone`. A systemd timer runs it daily at 03:30:

```bash
sudo cp deploy/systemd/goalzone-backup.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now goalzone-backup.timer
```

Restore a dump (test it on a scratch database first):

```bash
docker compose exec -T db sh -c 'createdb -U "$POSTGRES_USER" restore_test'
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d restore_test' < ~/backups/goalzone/<file>.sql
docker compose exec -T db sh -c 'dropdb -U "$POSTGRES_USER" restore_test'
```

The `systemd` unit has the project path and user name written in, so edit `deploy/systemd/goalzone-backup.service` before installing it on another machine.

## Monitoring

The bot exposes Prometheus metrics on port 8000 inside the Compose network. That port is not published to the host. Prometheus scrapes it every 15 seconds and is published only on `127.0.0.1:9090`. Its web UI has no authentication, so do not expose it to other machines.

| Metric | Type | Meaning |
|---|---|---|
| `goalzone_commands_total{command}` | counter | Handled bot commands |
| `goalzone_api_requests_total{result}` | counter | football-data.org requests: `ok`, `cache_hit`, `rate_limited`, `error` |
| `goalzone_last_heartbeat_timestamp_seconds` | gauge | Last successful Telegram check |

Alert rules live in `prometheus/alerts.yml`:

- `BotDown`: Prometheus cannot scrape the bot for 1 minute.
- `BotHeartbeatStale`: the bot is running, but has not reached Telegram for more than 3 minutes.
- `ApiRateLimited`: football-data.org returned HTTP 429 in the last 5 minutes.

Open `http://127.0.0.1:9090/alerts` to see them. I tested `BotDown` by stopping the bot container.

There is no Alertmanager, so alerts are not sent by email or Telegram, and there is no Grafana dashboard. The Prometheus query page is enough for this project. The Prometheus image is pinned to v3.16.0. It is not an LTS release: v3.13.5 (LTS) shipped a gRPC library with a known HIGH vulnerability (CVE-2026-84445), and v3.16.0 scanned clean with Trivy, so Dependabot updates must be reviewed regularly.

## Security notes

- Secrets live only in `.env`, which is git-ignored and excluded from the Docker image by `.dockerignore`. The `.env.example` file lists variable names only.
- The container runs as a non-root user, and `pip` is removed from the final image (Trivy reported vulnerabilities in the `pip` bundled with the base image).
- SQL queries use parameters, never string formatting.
- HTTP client logs are lowered to `WARNING`, so request URLs are not written to the logs.
- Trivy itself was compromised in a supply chain attack in March 2026. The workflow therefore pins the Trivy action to a full commit SHA and the Trivy binary to a fixed version instead of `latest`.
- GitHub's own actions (`checkout`, `setup-python`) are still pinned by tag. Pinning them by SHA is on the to-do list.

## Known limitations

- One league only (Premier League), and the free API plan returns slightly delayed scores.
- The cache is in memory and is lost when the bot restarts.
- No database migrations: `schema.sql` is applied only when the database volume is created.
- The bot is not hosted 24/7. It runs locally with Docker Compose.
- Database backups are stored on the same disk as the data. Copy them elsewhere for real protection.

## Project layout

| File | Purpose |
|---|---|
| `bot.py` | Telegram command handlers |
| `api.py` | football-data.org client with 60 s cache and error handling |
| `db.py` | PostgreSQL access (`psycopg`) |
| `teams.py` | Team lookup and match filtering |
| `formatters.py` | Message text and UTC to Tashkent time conversion |
| `config.py` | Reads settings from environment variables |
| `metrics.py` | Prometheus counters and gauge |
| `health.py` | Heartbeat used by the Docker health check |
| `schema.sql` | Database schema |
| `Dockerfile`, `docker-compose.yml` | Container setup |
| `tests/` | Pytest tests |
| `scripts/`, `deploy/systemd/` | Backup script and its systemd timer |
| `prometheus/` | Prometheus config and alert rules |

## Roadmap

- [x] MVP with `/start`, `/today`, `/table`
- [x] Modules, tests, `/fixtures`, in-memory cache
- [x] PostgreSQL: users and favorite team
- [x] Docker, Docker Compose, CI with lint, tests and security scans
- [x] Local operations practice: restart policy, health check, log limits, backups with a systemd timer
- [x] Prometheus metrics and alert rules (no Grafana, no Alertmanager)
