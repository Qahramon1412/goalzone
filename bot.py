import asyncio
import logging

import psycopg
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import api
import db
from config import TELEGRAM_BOT_TOKEN, check_config
from formatters import format_fixtures, format_table, format_today

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        await asyncio.to_thread(db.save_user, user.id, user.username)
    except psycopg.Error:
        logger.exception("Foydalanuvchini saqlab bo'lmadi")
    await update.message.reply_text(
        "GoalZone botiga xush kelibsiz! ⚽\n\n"
        "/today - bugungi Premier League o'yinlari\n"
        "/table - Premier League jadvali\n"
        "/fixtures - keyingi 7 kunlik o'yinlar"
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


async def fixtures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        matches = await asyncio.to_thread(api.get_fixtures)
    except api.APIError as e:
        await update.message.reply_text(str(e))
        return
    await update.message.reply_text(format_fixtures(matches))


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    check_config()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("table", table))
    app.add_handler(CommandHandler("fixtures", fixtures))
    app.run_polling()


if __name__ == "__main__":
    main()
