# 09_cashbox_execute_sale_steps.py
import httpx
import os
from datetime import datetime

GATEWAY_URL = "http://gateway:80"

async def run_cashbox_execute_sale_assertions():
    """Стадия 3: Открытие смены и проведение продажи по FIFO"""
    results = []
    if not os.path.exists("/tmp/test_product_id"):
        return ["❌ СБОЙ: Отсутствует буфер товара от Шага 07"]
        
    with open("/tmp/test_product_id", "r") as buf:
        product_id = int(buf.read())
        
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # 1. Открываем операционный день через шлюз
            day_res = await client.post("/api/v1/cash/days/open", json={"date": datetime.utcnow().isoformat()})
            if day_res.status_code != 201:
                raise Exception(f"Не удалось открыть кассовую смену. HTTP-{day_res.status_code}: {day_res.text}")
                
            # 2. Пробиваем розничный чек через шлюз
            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 500.00,
                "amount_cash": 500.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            res = await client.post("/api/v1/cash/sales", json=sale_payload)
            if res.status_code != 201:
                raise Exception(f"Ошибка проведения кассового чека при открытой смене. HTTP-{res.status_code}: {res.text}")
                
            results.append("✔️ Шаг 'Розничная FIFO-продажа успешно завершена' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ СБОЙ стадии проведения чека по FIFO: {str(e)}"]
            
    return results
