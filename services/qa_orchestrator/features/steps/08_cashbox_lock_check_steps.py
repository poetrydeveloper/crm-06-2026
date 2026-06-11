# 08_cashbox_lock_check_steps.py
import httpx
import os

# ИСПРАВЛЕНО: Запросы идут строго через официальный шлюз Nginx системы
GATEWAY_URL = "http://gateway:80"

async def run_cashbox_lock_check_assertions():
    """Стадия 2: Проверка блокировки чеков при закрытой кассе"""
    results = []
    if not os.path.exists("/tmp/test_product_id"):
        return ["❌ СБОЙ: Отсутствует буфер товара от Шага 07"]
        
    with open("/tmp/test_product_id", "r") as buf:
        product_id = int(buf.read())
        
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # =========================================================================
            # ИСПРАВЛЕНИЕ: Принудительно закрываем смену, оставшуюся от прошлых тестов,
            # чтобы перевести кассу в заблокированное (неоткрытое) состояние.
            # =========================================================================
            # Примечание: адрес ручки уточните по вашему Swagger ядра (например, /api/v1/cash/days/close)
            await client.post("/api/v1/cash/days/close") 
            # =========================================================================

            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 500.00,
                "amount_cash": 500.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            res = await client.post("/api/v1/cash/sales", json=sale_payload)
            
            if res.status_code != 400:
                raise Exception(f"Бэкенд вернул HTTP-{res.status_code} вместо HTTP-400. Тело ответа: {res.text}")
                
            results.append("✔️ Шаг 'Блокировка продаж при закрытой смене успешно подтверждена' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ СБОЙ стадии валидации блокировки кассы: {str(e)}"]
            
    return results
