import asyncio
import logging

import psycopg
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import api
import db
from config import TELEGRAM_BOT_TOKEN, check_config
from formatters import format_fixtures, format_table, format_today
from teams import filter_matches, find_team

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
        "/fixtures - keyingi 7 kunlik o'yinlar\n"
        "/favorite - sevimli jamoani tanlash (masalan: /favorite Arsenal)\n"
        "/my - sevimli jamoangizning yaqin o'yinlari"
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


async def favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Jamoa nomini yozing. Masalan: /favorite Arsenal"
        )
        return
    query = " ".join(context.args)
    try:
        rows = await asyncio.to_thread(api.get_table)
    except api.APIError as e:
        await update.message.reply_text(str(e))
        return
    team = find_team(rows, query)
    if team is None:
        await update.message.reply_text(
            "Bunday jamoa topilmadi. Nomini yoki /table dagi kodni "
            "yozing (masalan: ARS, MCI)."
        )
        return
    user = update.effective_user
    try:
        await asyncio.to_thread(db.save_user, user.id, user.username)
        await asyncio.to_thread(db.set_favorite_team, user.id, team)
    except psycopg.Error:
        logger.exception("Sevimli jamoani saqlab bo'lmadi")
        await update.message.reply_text(
            "Hozir saqlab bo'lmadi. Birozdan keyin urinib ko'ring."
        )
        return
    await update.message.reply_text(f"Sevimli jamoangiz: {team} ✅")


async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        row = await asyncio.to_thread(db.get_user, user.id)
    except psycopg.Error:
        logger.exception("Foydalanuvchini o'qib bo'lmadi")
        await update.message.reply_text(
            "Hozir ma'lumotlar bazasiga ulanib bo'lmadi. Keyinroq urinib ko'ring."
        )
        return
    if row is None or row[2] is None:
        await update.message.reply_text(
            "Avval sevimli jamoani tanlang. Masalan: /favorite Arsenal"
        )
        return
    team = row[2]
    try:
        today_matches = await asyncio.to_thread(api.get_today)
        upcoming = await asyncio.to_thread(api.get_fixtures)
    except api.APIError as e:
        await update.message.reply_text(str(e))
        return
    team_matches = filter_matches(today_matches + upcoming, team)
    if not team_matches:
        await update.message.reply_text(
            f"{team} ning keyingi 7 kunda Premier League o'yini yo'q."
        )
        return
    await update.message.reply_text(format_fixtures(team_matches))


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
    app.add_handler(CommandHandler("favorite", favorite))
    app.add_handler(CommandHandler("my", my))
    app.run_polling()


if __name__ == "__main__":
    main()
