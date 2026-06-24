FROM python:3.11-slim

# 1. Защита от буферизации логов и генерации мусорных .pyc файлов
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 2. Оптимальное кэширование pip-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем исходный код бэкенда
COPY . .

# 4. Запуск основного ядра CRM
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]