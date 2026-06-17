# services/qa_orchestrator/features/backend/steps/08_cashbox_lock_check_steps.py (ЧАСТЬ 1 ИЗ 2)
import httpx
from utils.validators import safe_header

GATEWAY_URL = "http://gateway:80"

async def run_08_cashbox_lock_check_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль блокировки чеков без открытой смены.
    СТРОГАЯ ИЗОЛЯЦИЯ: Принудительное закрытие кассовых дней перед стартом.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CS-0008-01")}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 1. 🛡️ SETUP: Гарантированно закрываем кассовую смену, если она была открыта
            # Шлем запрос на ручку закрытия, чтобы в СУБД не осталось активных смен
            await client.post("/api/v1/cash/days/close")

            # 2. ИСПОЛНЕНИЕ: Кассир пытается отправить чек продажи по схеме CashSaleCreate
            sale_payload = {
                "product_id": 1,
                "sale_price": 500.0,
                "amount_cash": 500.0,
                "amount_card": 0.0,
                "amount_credit": 0.0
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Попытка проведения продажи при закрытой смене")}
            response = await client.post("/api/v1/cash/sales", json=sale_payload, headers=step_headers)
# services/qa_orchestrator/features/backend/steps/08_cashbox_lock_check_steps.py (ЧАСТЬ 2 ИЗ 2)
            # 3. 🛡️ ЖЕСТКИЙ АССЕРТ БЛОКИРОВКИ СМЕНЫ
            # Твой роутер routers/cash.py при закрытой смене обязан выбросить HTTP 400
            if response.status_code == 400:
                results.append("   ✅ Когда Кассир пытается пробить чек продажи при неоткрытом кассовом дне")
                results.append("   ✅ Тогда Система блокирует операцию и возвращает статус 400 с описанием ошибки смены")
            else:
                return [f"❌ КРИТИЧЕСКИЙ СБОЙ ФИНАНСОВОЙ БЕЗОПАСНОСТИ: Бэкенд пропустил продажу или вернул код {response.status_code} вместо 400. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ВОСЬМОЙ ИСТОРИИ: {str(e)}"]

    return results
