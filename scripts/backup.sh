#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-$HOME/backups/goalzone}"
KEEP="${KEEP:-7}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
cd "$PROJECT_DIR"

OUT="$BACKUP_DIR/goalzone-$(date +%F-%H%M%S).sql"
TMP="$OUT.partial"
trap 'rm -f "$TMP"' EXIT

docker compose exec -T db sh -c \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists' > "$TMP"

if ! grep -q "PostgreSQL database dump complete" "$TMP"; then
  echo "Xato: zaxira nusxa to'liq emas" >&2
  exit 1
fi

mv "$TMP" "$OUT"
ls -1t "$BACKUP_DIR"/goalzone-*.sql | tail -n +$((KEEP + 1)) | xargs -r rm --
echo "OK: $OUT"
