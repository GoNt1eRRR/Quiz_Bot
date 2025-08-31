# Vk и Tg бот для викторины по истории

Боты помогают проводить тестирование и автоматически проверять результаты с возможностью узнать ответ на вопрос. 

Пример работы бота в TG: 

![tg](https://github.com/user-attachments/assets/0de72a99-c26a-4b3f-83c3-0c20af4e78f6)

Пример работы бота в VK: 

![VK](https://github.com/user-attachments/assets/57ffb702-764a-4670-9d6c-9f2491e9c9c4)

Ссылки на примеры:
- [Telegram](https://t.me/quiz_devmantask_bot)
- [Vk](https://vk.com/club232414925)

## Требования

Для запуска скрипта необходимы:

- Python 3.8+
- Установленные зависимости из `requirements.txt`

## Установка

1. Склонируйте репозиторий проекта:
    ```bash
    git clone https://github.com/GoNt1eRRR/Quiz_bot.git
    ```

2. Создайте виртуальное окружение:
    ```bash
    python -m venv .venv
    ```

3. Активируйте виртуальное окружение:
    - На Windows:
        ```bash
        .venv\Scripts\activate
        ```
    - На Linux и MacOS:
        ```bash
        source .venv/bin/activate
        ```

4. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

## Конфигурация
1. Получите токен для тг бота через [BotFather](https://telegram.me/BotFather)
   
2. Получите токен для вк бота в меню “Работа с API” в настройках вашего сообщества

3. PATH_TO_QUESTIONS - путь с названием и расширением файла с вопросами. Используется кодировка KOI8-R. Скачать примеры вопросов можно [здесь](https://drive.google.com/file/d/12ssZb8NWtz7hQqwTWNdbyI-2xzPOHV0I/view?usp=sharing)

4. REDIS_HOST, REDIS_PORT, REDIS_PASSWORD - данные для подключения к базе данных Redis. Можно получить на сайте [Redis](https://redis.io/)

**Бот не будет работать без токенов!**

Создайте файл `.env` в корне проекта и добавьте туда ваши данные. 

Пример файла `.env`:

```
TG_TOKEN= Ваш тг токен
VK_TOKEN= Ваш вк токен
REDIS_HOST= данные бд редиса
REDIS_PORT= данные бд редиса
REDIS_PASSWORD= данные бд редиса
PATH_TO_QUESTIONS= путь к папке с файлами вопросов
```

## Запуск 
Запуск скриптов осуществляется через консоль:
```
python tg_bot.py
python vk_bot.py
```
