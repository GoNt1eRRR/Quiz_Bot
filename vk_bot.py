import random
import re
import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from utils import get_questions
from redis_db import connect_to_db


def normalize_answer(text: str) -> str:
    text = text.lower().strip()
    text = text.split(".", 1)[0]
    text = text.split("(", 1)[0]
    text = re.sub(r"\s+", " ", text)
    text = text.replace("ё", "е")
    return text


def give_up(event, vk_api, keyboard, db, questions):
    answer = db.get(f"answer:{event.user_id}")
    if not answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Ты ещё не задавал вопрос! Нажми "Новый вопрос"',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )
        return

    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Правильный ответ: "{answer}"',
        random_id=random.randint(1, 1000),
    )

    get_new_question(event, vk_api, keyboard, db, questions)


def check_answer(event, vk_api, keyboard, db):
    correct = db.get(f"answer:{event.user_id}")
    if not correct:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Сначала нажми "Новый вопрос"',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )
        return

    if normalize_answer(event.text) == normalize_answer(correct):
        vk_api.messages.send(
            user_id=event.user_id,
            message="Правильно! 🎉\nДля следующего вопроса нажми «Новый вопрос»",
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )
        db.incr(f"score:{event.user_id}")
        db.delete(f"answer:{event.user_id}")
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message="Неправильно… Попробуешь ещё раз? 🤔",
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )


def get_new_question(event, vk_api, keyboard, db, questions):
    question, answer = random.choice(list(questions.items()))
    db.set(f"answer:{event.user_id}", answer)

    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def show_score(event, vk_api, keyboard, db):
    score = db.get(f"score:{event.user_id}") or 0
    vk_api.messages.send(
        user_id=event.user_id,
        message=f"Твой счёт: {score} 🧮",
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


if __name__ == "__main__":
    env = Env()
    env.read_env()

    vk_session = vk.VkApi(token=env("VK_TOKEN"))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    questions = get_questions(env.str("PATH_TO_QUESTIONS"))

    db = connect_to_db(
        host=env.str("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        password=env.str("REDIS_PASSWORD")
    )

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.PRIMARY)

    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue

        if event.text == "Сдаться":
            give_up(event, vk_api, keyboard, db, questions)
        elif event.text == "Новый вопрос":
            get_new_question(event, vk_api, keyboard, db, questions)
        elif event.text == "Мой счёт":
            show_score(event, vk_api, keyboard, db)
        elif event.text in ("/start", "Старт", "Привет"):
            vk_api.messages.send(
                user_id=event.user_id,
                message="Привет! Я бот для викторин 🎉",
                random_id=random.randint(1, 1000),
                keyboard=keyboard.get_keyboard()
            )
        else:
            check_answer(event, vk_api, keyboard, db)
