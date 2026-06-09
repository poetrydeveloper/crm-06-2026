FROM python:3.11-alpine

WORKDIR /app

# Устанавливаем системные зависимости для сборки бинарных пакетов (если понадобятся)
RUN apk add --no-cache gcc musl-dev postgresql-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем FastAPI сервер оркестратора, чтобы мы могли вызывать тесты кнопкой или через API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]

