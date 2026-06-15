import os
import random
import pandas as pd
import joblib

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =====================
# LOAD MODEL + DATA
# =====================

TOKEN = os.getenv("BOT_TOKEN")

model = joblib.load("best_model.pkl")
movies = pd.read_csv("movies.csv")


# =====================
# RECOMMENDATION ENGINE
# =====================

def get_top_n(model, movies_df, user_id, n=10):
    movie_ids = movies_df["movieId"].unique()

    predictions = []
    for movie_id in movie_ids:
        pred = model.predict(user_id, movie_id)
        predictions.append((movie_id, pred.est))

    predictions.sort(key=lambda x: x[1], reverse=True)

    top_ids = [m[0] for m in predictions[:n]]
    top_scores = dict(predictions[:n])

    result = movies_df[movies_df["movieId"].isin(top_ids)].copy()
    result["score"] = result["movieId"].map(top_scores)

    return result.sort_values("score", ascending=False)


# =====================
# KEYBOARD
# =====================

keyboard = [
    ["🎬 Топ 10 фильмов", "🤖 Рекомендации"],
    ["🔎 Найти фильм", "🎲 Фильм дня"],
    ["📊 Статистика"],
]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# =====================
# COMMANDS
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Привет! Я бот-рекомендатель фильмов.\nВыбери действие 👇",
        reply_markup=markup,
    )


async def top_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = 1

    top_df = get_top_n(model, movies, user_id, n=10)

    text = "🎬 ТОП-10 фильмов:\n\n"

    for _, row in top_df.iterrows():
        text += f"⭐ {row['title']} — {row['score']:.2f}\n"

    await update.message.reply_text(text)


async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = 1

    top_df = get_top_n(model, movies, user_id, n=5)

    text = "🤖 Персональные рекомендации:\n\n"

    for _, row in top_df.iterrows():
        text += f"🎬 {row['title']}\n⭐ {row['score']:.2f}\n\n"

    await update.message.reply_text(text)


async def find_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args).lower()

    if not query:
        await update.message.reply_text("Напиши: /find название фильма")
        return

    results = movies[movies["title"].str.lower().str.contains(query)]

    if results.empty:
        await update.message.reply_text("Фильм не найден 😢")
        return

    text = "🔎 Найдено:\n\n"

    for _, row in results.head(5).iterrows():
        text += f"🎬 {row['title']}\n"

    await update.message.reply_text(text)


async def movie_of_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie = movies.sample(1).iloc[0]

    await update.message.reply_text(
        f"🎲 Фильм дня:\n\n🎬 {movie['title']}"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Статистика:\n\n"
        f"🎬 Фильмов: {len(movies)}\n"
        f"🤖 Модель: SVD (Surprise)\n"
        f"⚡ Статус: активен"
    )


# =====================
# BUTTON HANDLER
# =====================

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎬 Топ 10 фильмов":
        await top_movies(update, context)

    elif text == "🤖 Рекомендации":
        await recommend(update, context)

    elif text == "🔎 Найти фильм":
        await update.message.reply_text("Напиши: /find название фильма")

    elif text == "🎲 Фильм дня":
        await movie_of_day(update, context)

    elif text == "📊 Статистика":
        await stats(update, context)


# =====================
# MAIN
# =====================

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top_movies))
    app.add_handler(CommandHandler("recommend", recommend))
    app.add_handler(CommandHandler("find", find_movie))
    app.add_handler(CommandHandler("stats", stats))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
