# Використовуємо офіційний Python-образ
FROM python:3.11-slim

# Встановлюємо системні залежності, щоб asyncpg міг зібратися
RUN apt-get update && apt-get install -y gcc libffi-dev libpq-dev build-essential && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли проекту
COPY . .

# Встановлюємо залежності
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Вказуємо команду запуску
CMD ["python", "bot.py"]
