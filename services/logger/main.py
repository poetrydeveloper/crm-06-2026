# services/logger/main.py
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional
import logging

app = FastAPI(title="CRM Logger Service", version="1.0.0")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

_GLOBAL_LOGS_STORAGE = []


class LogMessage(BaseModel):
    service: str
    level: str
    message: str
    operation_code: Optional[str] = Field(None, description="Код ERP-операции (например, '0401', '0501')")


@app.post("/api/v1/log")
async def receive_log(payload: LogMessage):
    log_text = f"[{payload.service.upper()}] [{payload.level.upper()}] {payload.message}"
    logging.info(log_text)

    op_code = payload.operation_code
    if not op_code:
        if "0501" in payload.message or "возврат" in payload.message.lower():
            op_code = "0501"
        elif "0401" in payload.message or "продажа" in payload.message.lower():
            op_code = "0401"

    now_time = datetime.now(timezone.utc).isoformat()

    _GLOBAL_LOGS_STORAGE.append({
        "service": payload.service,
        "level": payload.level,
        "message": payload.message,
        "operation_code": op_code or "0000",
        "timestamp": now_time
    })

    return {"status": "logged", "timestamp": now_time}


@app.get("/api/v1/logs/search", status_code=200)
async def search_logs_by_operation(operation_code: str = Query(..., description="Код операции, например 0501")):
    filtered_logs = [log for log in _GLOBAL_LOGS_STORAGE if log["operation_code"] == operation_code]
    return filtered_logs