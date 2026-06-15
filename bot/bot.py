import os
import joblib
import pandas as pd

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =====================
# TOKEN
# =====================
TOKEN = os.getenv("BOT_TOKEN")

# =====================
# DATA + MODEL
# =====================
model = joblib.load("best_model.pkl")
movies = pd.read_csv("movies.csv")

# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⭐ Топ-10 фильмов", callback_data="top10")],
        [InlineKeyboardButton("🔍 Найти фильм", callback_data="search")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]

    await update.message.reply_text(
        "🎬 Привет! Я Movie Recommender Bot\nВыбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =====================
# BUTTONS
# =====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ⭐ TOP-10
    if query.data == "top10":
        user_id = 1  # демо-юзер (позже улучшим)

        all_movies = movies["movieId"].unique()

        preds = [
            (mid, model.predict(user_id, mid).est)
            for mid in all_movies
        ]

        top = sorted(preds, key=lambda x: x[1], reverse=True)[:10]

        text = "⭐ Топ-10 рекомендаций:\n\n"

        for mid, score in top:
            title = movies[movies["movieId"] == mid]["title"].values[0]
            text += f"{title} — ⭐ {score:.2f}\n"

        await query.message.reply_text(text)

    # 🔍 SEARCH MODE
    elif query.data == "search":
        await query.message.reply_text("🔎 Напиши название фильма:")

    # ℹ️ HELP
    elif query.data == "help":
        await query.message.reply_text(
            "📌 Как пользоваться:\n"
            "• Топ-10 — рекомендации\n"
            "• Поиск — просто введи название фильма\n"
        )

# =====================
# TEXT SEARCH
# =====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    results = movies[movies["title"].str.lower().str.contains(text)]

    if len(results) == 0:
        await update.message.reply_text("❌ Ничего не найдено")
        return

    msg = "🔎 Найдено:\n\n"

    for _, row in results.head(5).iterrows():
        msg += f"{row['title']}\n"

    await update.message.reply_text(msg)

# =====================
# MAIN
# =====================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
