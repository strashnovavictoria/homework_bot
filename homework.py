import logging
import os
from dotenv import load_dotenv
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from telegram import Bot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID= os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 0
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

current_timestamp = int(time.time())


def send_message(bot, message):
     
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID, 
        text=message
    )
def get_api_answer(current_timestamp):
    """делает запрос к единственному эндпоинту API-сервиса."""

    params = {'from_date': current_timestamp}
    homeworks = requests.get(ENDPOINT, headers=HEADERS, params=params)
    response = homeworks.json()
    status_code = homeworks.status_code
    if status_code != HTTPStatus.OK:
        message = 'API недоступен'
        logging.error(message)
        raise HTTPStatusCodeIncorrect(message)
    return response 

def check_response(response):
    """проверяет ответ API на корректность."""
  

    if not response:
        raise Exception('Словарь пустой')
    if 'homeworks' not in response:
        raise ('Нет ключа "homeworks"')
    if type(response) is not dict:
        raise TypeError ('Не словарь')  
    try:   
        homework = response['homeworks'][0]
    except IndexError:
        logging.error('Пустой')
        raise Exception ('Пустой')
    return homework


def parse_status(homework):
    """извлекает из информации о конкретной домашней работе статус этой работы."""

    if type(homework) is not dict:
        raise KeyError ('Это не словарь!')
    homework_status = homework['status']
    homework_name = homework['homework_name']
    if homework_name is None:
        message = 'В ответе от сервера пришли пустые данные.'
        logger.error(message, exc_info=True)
        raise KeyError
    elif homework_status is None:
        message = 'В ответе от сервера нет данных о статусе.'
        logger.error(message, exc_info=True)
        raise KeyError
    elif homework_status not in HOMEWORK_STATUSES:
        message = 'В ответе от сервера неизвестный статус!'
        logger.error(message, exc_info=True)
        raise KeyError
    else:
        result = HOMEWORK_STATUSES[homework_status]
        messange = (f'Изменился статус проверки работы "{homework_name}". {result}')
        return messange


def check_tokens() -> bool:
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """главная фунция.общий ход работы"""

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if not check_tokens:
        raise KeyError ('Нет переменных окружения')
    try:
        response = get_api_answer(current_timestamp)
        homework = check_response(response)
        messange = parse_status(homework)
        send_message(bot,messange)
        time.sleep(RETRY_TIME)
    except:
        messange = 'Ответа нет'
        logging.critical(messange)
        send_message(bot,messange)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

