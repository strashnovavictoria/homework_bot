# homework_bot
Telegram-бот раз в 10 минут обращается к API сервиса Практикум.Домашка и получает информацию об изменениях статусов домашних работ на Яндекс.Практикуме 


## Как запустить проект:
Запуск проекта на локальном компьютере
Клонировать репозиторий и перейти в него в командной строке:

Создать в корневой папке проекта файл с названием ".env" и следующим содержанием:

PRACTICUM_TOKEN=<токен для API сервиса Практикум.Домашка>
TELEGRAM_TOKEN=<токен для работы с Bot API>
TELEGRAM_CHAT_ID=<ID вашего Telegram-аккаунта>**

python -m venv env

Установить зависимости из файла requirements.txt:

python -m pip install --upgrade pip
pip install -r requirements.txt
Локально запустить бота:

Остановить работу бота можно командой Ctrl + C.

### Используемые технологии:

Python 3.7, python-telegram-bot

#### Автор:
- Виктория Страшнова [strashnovavictoria](https://github.com/strashnovavictoria)
