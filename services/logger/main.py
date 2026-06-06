from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import logging

app = FastAPI(title="CRM Logger Service", version="1.0.0")

# Настраиваем стандартный логгер Python для вывода в консоль
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LogMessage(BaseModel):
    service: str      # Имя сервиса, который отправил лог (например, 'core')
    level: str        # INFO, WARNING, ERROR
    message: str      # Текст сообщения

@app.post("/api/v1/log")
async def receive_log(payload: LogMessage):
    # Форматируем и выводим лог в консоль контейнера
    log_text = f"[{payload.service.upper()}] [{payload.level.upper()}] {payload.message}"
    logging.info(log_text)
    
    # Здесь в будущем можно добавить запись в файл или отдельную БД MongoDB/ClickHouse
    return {"status": "logged", "timestamp": datetime.utcnow()}
