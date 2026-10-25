import asyncio
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import api
from config import TELEGRAM_BOT_TOKEN, check_config

UZ_TZ = timezone(timedelta(hours=5))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "GoalZone botiga xush kelibsiz! ⚽\n\n"
        "/today - bugungi Premier League o'yinlari\n"
        "/table - Premier League jadvali"
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        matches = await asyncio.to_thread(api.get_today)
    except api.APIError as e:
        await update.message.reply_text(str(e))
        return
    if not matches:
        await update.message.reply_text("Bugun Premier League o'yinlari yo'q.")
        return
    lines = ["Bugungi o'yinlar (Toshkent vaqti):\n"]
    for m in matches:
        utc_time = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
        local_time = utc_time.astimezone(UZ_TZ).strftime("%H:%M")
        home = m["homeTeam"]["shortName"]
        away = m["awayTeam"]["shortName"]
        lines.append(f"{local_time}  {home} - {away}")
    await update.message.reply_text("\n".join(lines))


async def table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rows = await asyncio.to_thread(api.get_table)
    except api.APIError as e:
        await update.message.reply_text(str(e))
        return
    lines = [" #  Jamoa  O'  Och"]
    for r in rows:
        lines.append(
            f"{r['position']:>2}  {r['team']['tla']}  {r['playedGames']:>2}  {r['points']:>3}"
        )
    text = "<pre>" + "\n".join(lines) + "</pre>"
    await update.message.reply_text(text, parse_mode="HTML")


def main():
    check_config()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("table", table))
    app.run_polling()


if __name__ == "__main__":
    main()
