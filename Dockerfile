# Базовый образ для Python
FROM python:3.10

# Копирование исходного кода в контейнер
COPY . /app

# Установка рабочей директории
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Установка переменных окружения
ENV TOKEN=YOUR_TELEGRAM_TOKEN
ENV DB_HOST=YOUR_DB_HOST
ENV DB_NAME=YOUR_DB_NAME
ENV DB_USER=YOUR_DB_USER
ENV DB_PASSWORD=YOUR_DB_PASSWORD

# Запуск бота
CMD ["python", "bot.py"]