import random
from enum import Enum, auto
from environs import Env
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext, ConversationHandler
)
from redis_db import connect_to_db
from utils import get_questions
from functools import partial

QUESTIONS = {}


class States(Enum):
    NEW_QUESTION = auto()
    WAITING_FOR_ANSWER = auto()


def normalize_answer(answer: str) -> str:
    answer = answer.split(".", 1)[0]
    answer = answer.split("(", 1)[0]
    return answer.strip().lower()


def start(update: Update, context: CallbackContext):
    keyboard = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счёт"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Привет! Я бот для викторин!", reply_markup=reply_markup)
    return States.NEW_QUESTION


def handle_new_question_request(update: Update, context: CallbackContext, db, questions):
    chat_id = update.effective_chat.id
    question, answer = random.choice(list(questions.items()))
    db.set(f"user:{chat_id}:answer", answer)
    update.message.reply_text(question)
    return States.WAITING_FOR_ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = context.bot_data["db"]

    user_answer = normalize_answer(update.message.text)
    correct_answer = normalize_answer(db.get(f"user:{chat_id}:answer") or "")

    if user_answer == correct_answer:
        update.message.reply_text(
            "Правильно! 🎉\nДля следующего вопроса нажми «Новый вопрос»"
        )
        db.incr(f"user:{chat_id}:score")
        return States.NEW_QUESTION
    else:
        update.message.reply_text("Неправильно… Попробуешь ещё раз? 🤔")
        return States.WAITING_FOR_ANSWER


def handle_give_up(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = context.bot_data["db"]

    answer = db.get(f"user:{chat_id}:answer")
    if answer:
        update.message.reply_text(f"Правильный ответ: {answer}")
    return handle_new_question_request(update, context)


def handle_score(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = context.bot_data["db"]

    score = db.get(f"user:{chat_id}:score") or 0
    update.message.reply_text(f"Твой счёт: {score} 🧮")
    return States.NEW_QUESTION


def main():
    env = Env()
    env.read_env()

    db = connect_to_db(
        host=env("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        password=env("REDIS_PASSWORD")
    )
    questions = get_questions("quiz-questions")

    token = env("TG_TOKEN")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.NEW_QUESTION: [
                MessageHandler(Filters.regex("^Новый вопрос$"),partial(handle_new_question_request, db=db, questions=questions)),
                MessageHandler(Filters.regex("^Мой счёт$"), handle_score),
            ],
            States.WAITING_FOR_ANSWER: [
                MessageHandler(Filters.regex("^Сдаться$"), handle_give_up),
                MessageHandler(Filters.regex("^Новый вопрос$"), handle_new_question_request),
                MessageHandler(Filters.regex("^Мой счёт$"), handle_score),
                MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt),
            ],
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
