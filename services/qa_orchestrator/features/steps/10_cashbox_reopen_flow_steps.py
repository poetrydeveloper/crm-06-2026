# 10_cashbox_reopen_flow_steps.py
import httpx
import os
from datetime import datetime

GATEWAY_URL = "http://gateway:80"

async def run_cashbox_reopen_flow_assertions():
    """Стадия 4: Тестирование ручки /reopen и дозаписи чеков"""
    results = []
    
    if not os.path.exists("/tmp/test_product_id"):
        return ["❌ СБОЙ: Отсутствует буфер товара"]
    with open("/tmp/test_product_id", "r") as buf:
        product_id = int(buf.read())

    # Создаем обязательное тело запроса с датой, которое требует ядро бэкенда
    payload_open = {"date": datetime.utcnow().isoformat()}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # 1. Пытаемся открыть день
            open_res = await client.post("/api/v1/cash/days/open", json=payload_open)
            
            if open_res.status_code == 201:
                cash_day_id = open_res.json().get("cash_day_id")
            elif open_res.status_code == 400 and "уже есть открытая" in open_res.text:
                # Если день остался открыт от 9-го теста, закроем его, чтобы открыть заново и получить ID
                await client.post("/api/v1/cash/days/close")
                retry_open = await client.post("/api/v1/cash/days/open", json=payload_open)
                cash_day_id = retry_open.json().get("cash_day_id")
            else:
                raise Exception(f"Не удалось инициализировать день. Код: {open_res.status_code}, Текст: {open_res.text}")

            # 2. Теперь закрываем его перед проверкой reopen
            await client.post("/api/v1/cash/days/close")

            # 3. ДЕРГАЕМ РУЧКУ REOPEN
            reopen_res = await client.post(f"/api/v1/cash/days/{cash_day_id}/reopen")
            if reopen_res.status_code != 200:
                raise Exception(f"Ручка reopen вернула ошибку {reopen_res.status_code}")

            # 4. Проверяем дозапись чека по FIFO на переоткрытой кассе
            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 500.00,
                "amount_cash": 500.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            sale_res = await client.post("/api/v1/cash/sales", json=sale_payload)
            
            if sale_res.status_code != 201:
                raise Exception(f"Дозапись не удалась. Код: {sale_res.status_code}")

            results.append("✔️ Шаг 'Переоткрытие кассового дня и дозапись чеков' — ПРОЙДЕН")
            
            # Чистим за собой систему — закрываем день окончательно
            await client.post("/api/v1/cash/days/close")

        except Exception as e:
            return [f"❌ СБОЙ сценария переоткрытия смены: {str(e)}"]
            
    return results
