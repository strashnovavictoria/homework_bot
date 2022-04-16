import logging
import os
import sys
from dotenv import load_dotenv
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram

logger = logging.getLogger('homework.py')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('main.log',
                              maxBytes=50000000, backupCount=5)
logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(name)s,'
                              '%(message)s, %(funcName)s, %(lineno)d')
handler.setFormatter(formatter)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 0
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICT = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

current_timestamp = int(time.time())


class HTTPStatusCodeIncorrect(Exception):
    """Создаем исключение."""

    pass


class SendMessageEror(Exception):
    """Создаем исключение."""

    pass


class TokenError(Exception):
    """Создаем исключение."""

    pass


def send_message(bot, message):
    """Фунция для отправки сообщений."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': current_timestamp}
    homeworks = requests.get(ENDPOINT, headers=HEADERS, params=params)
    response = homeworks.json()
    status_code = homeworks.status_code
    if status_code != HTTPStatus.OK:
        message = f'API недоступен, код ошибки: {status_code}'
        logger.error(message)
        raise HTTPStatusCodeIncorrect(message)
    return response


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Не словарь')
    if 'current_date' not in response:
        raise Exception('Нет ключа "current_date"')
    if 'homeworks' not in response:
        raise Exception('Нет ключа "homeworks"')
    try:
        homework = response['homeworks'][0]
    except IndexError:
        raise Exception('Некорректные данные')
    return homework


def parse_status(homework):
    """Извлекает статус работы."""
    if not isinstance(homework, dict):
        raise KeyError('Это не словарь!')
    homework_status = homework['status']
    homework_name = homework['homework_name']
    if not homework_name:
        raise KeyError('В ответе от сервера пришли пустые данные.')
    elif homework_status is None:
        raise KeyError('В ответе от сервера нет данных о статусе.')
    elif homework_status not in HOMEWORK_VERDICT:
        raise KeyError('В ответе от сервера неизвестный статус!')
    verdict = HOMEWORK_VERDICT[homework_status]
    message = (f'Изменился статус проверки работы "{homework_name}".'
               f'{verdict}')
    return message


def check_tokens() -> bool:
    """Проверяем переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Главная фунция.общий ход работы."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if not check_tokens:
        logger.error('Нет переменных окружения')
        sys.exit()
    try:
        response = get_api_answer(current_timestamp)
        homework = check_response(response)
        message = parse_status(homework)
        try:
            send_message(bot, message)
            logger.info(f'Бот отправил сообщение: {message}')
        except SendMessageEror as error:
            logger.error(f'Ошибка при отправке сообщения: {error}')
    except Exception:
        message = 'Ответа нет'
        logging.error(message)
        send_message(bot, message)
    finally:
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
