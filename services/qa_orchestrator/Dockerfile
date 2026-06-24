FROM python:3.11-alpine

WORKDIR /app

# 1. Защита от буферизации логов тестов
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 2. Устанавливаем только необходимые системные библиотеки
RUN apk add --no-cache gcc musl-dev postgresql-dev libffi-dev

# 3. Эффективное кэширование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем исходный код оркестратора
COPY . .

# 5. 🔥 ИСПРАВЛЕНО: Убран флаг --reload для предотвращения срыва тестов при записи отчетов
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
