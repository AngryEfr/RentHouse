# Базовый образ для Python
FROM python:3.10

# Копирование исходного кода в контейнер
COPY . /app

# Установка рабочей директории
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Запуск бота
CMD ["python", "bot.py"]

#build -t somename .