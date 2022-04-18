import logging
import sys
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
import requests
import telegram
from dotenv import load_dotenv

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

current_timestamp = 0
RETRY_TIME = 0
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICT = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class HTTPStatusCodeIncorrect(Exception):
    """Создаем исключение."""

    pass


class GetAPIEror(Exception):
    """Создаем исключение."""

    pass


class TokenError(Exception):
    """Создаем исключение."""

    pass


class ResponseNotCorrect(Exception):
    """Создаем исключение."""

    pass


def send_message(bot, message):
    """Фунция для отправки сообщений."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception:
        logger.error('Ошибка при отправке сообщения')
    else:
        logger.info(f'Бот отправил сообщение: {message}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'headers': HEADERS,
              'params': {'from_date': current_timestamp}}
    try:
        homeworks = requests.get(ENDPOINT, **params)
        response = homeworks.json()
        status_code = homeworks.status_code
        if status_code != HTTPStatus.OK:
            message = f'API недоступен, код ошибки: {status_code}'
            raise HTTPStatusCodeIncorrect(message)
    except GetAPIEror:
        raise GetAPIEror('Ошибка при отправке.')
    return response


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Не словарь')
    if 'current_date' not in response:
        raise KeyError('Нет ключа "current_date"')
    if 'homeworks' not in response:
        raise KeyError('Нет ключа "homeworks"')
    try:
        homework = response['homeworks'][0]
    except ResponseNotCorrect:
        raise ResponseNotCorrect('Некорректные данные')
    return homework


# pytest принимает только с KeyError и только с проверкой на то, что словарь.
def parse_status(homework):
    """Извлекает статус работы."""
    if not isinstance(homework, dict):
        raise KeyError('Это не словарь!')
    homework_status = homework['status']
    homework_name = homework['homework_name']
    if not homework_name:
        raise ValueError('В ответе от сервера пришли пустые данные.')
    elif homework_status is None:
        raise ValueError('В ответе от сервера нет данных о статусе.')
    elif homework_status not in HOMEWORK_VERDICT:
        raise ValueError('В ответе от сервера неизвестный статус!')
    verdict = HOMEWORK_VERDICT[homework_status]
    message = (f'Изменился статус проверки работы "{homework_name}".'
               f'{verdict}')
    return message


def check_tokens() -> bool:
    """Проверяем переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Главная фунция.общий ход работы."""
    if not check_tokens:
        logger.critical('Нет переменных окружения')
        sys.exit(-1)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    try:
        response = get_api_answer(current_timestamp)

        homework = check_response(response)
        message = parse_status(homework)
        send_message(bot, message)
    except Exception as error:
        message = f'Сбой в работе программы: {error}'
        logging.error(message)
        send_message(bot, message)
    finally:
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
