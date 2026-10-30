from datetime import datetime, timedelta, timezone

UZ_TZ = timezone(timedelta(hours=5))


def _to_local(utc_date, fmt):
    utc_time = datetime.fromisoformat(utc_date)
    return utc_time.astimezone(UZ_TZ).strftime(fmt)


def format_today(matches):
    if not matches:
        return "Bugun Premier League o'yinlari yo'q."
    lines = ["Bugungi o'yinlar (Toshkent vaqti):\n"]
    for m in matches:
        local_time = _to_local(m["utcDate"], "%H:%M")
        home = m["homeTeam"]["shortName"]
        away = m["awayTeam"]["shortName"]
        lines.append(f"{local_time}  {home} - {away}")
    return "\n".join(lines)


def format_fixtures(matches):
    if not matches:
        return "Keyingi 7 kunda Premier League o'yinlari yo'q."
    lines = ["Yaqin o'yinlar (Toshkent vaqti):\n"]
    for m in matches:
        local_time = _to_local(m["utcDate"], "%d.%m %H:%M")
        home = m["homeTeam"]["shortName"]
        away = m["awayTeam"]["shortName"]
        lines.append(f"{local_time}  {home} - {away}")
    return "\n".join(lines)


def format_table(rows):
    lines = [" #  Jamoa  O'  Och"]
    for r in rows:
        lines.append(
            f"{r['position']:>2}  {r['team']['tla']}  {r['playedGames']:>2}  {r['points']:>3}"
        )
    return "<pre>" + "\n".join(lines) + "</pre>"
