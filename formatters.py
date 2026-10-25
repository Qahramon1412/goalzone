from datetime import datetime, timedelta, timezone

UZ_TZ = timezone(timedelta(hours=5))


def format_today(matches):
    if not matches:
        return "Bugun Premier League o'yinlari yo'q."
    lines = ["Bugungi o'yinlar (Toshkent vaqti):\n"]
    for m in matches:
        utc_time = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
        local_time = utc_time.astimezone(UZ_TZ).strftime("%H:%M")
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
