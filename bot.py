import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import api
from config import TELEGRAM_BOT_TOKEN, check_config
from formatters import format_table, format_today


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
    await update.message.reply_text(format_today(matches))


async def table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rows = await asyncio.to_thread(api.get_table)
    except api.APIError as e:
        await update.message.reply_text(str(e))
        return
    await update.message.reply_text(format_table(rows), parse_mode="HTML")


def main():
    check_config()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("table", table))
    app.run_polling()


if __name__ == "__main__":
    main()
