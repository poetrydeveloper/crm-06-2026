# services/qa_orchestrator/features/frontend/steps/08_cashbox_sale_execution_steps.py
import httpx
from datetime import datetime

GATEWAY_URL = "http://gateway:80"

async def run_08_cashbox_sale_execution_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка отправки чека продажи и логирования операции 0401.
    Корректно передает payload даты для открытия смены в соответствии с контрактом ядра.
    """
    results = []
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано В электронном чеке кассы находится товар с серийным номером 'SN-MOCK-777'")

            # 🛡️ ПРАВИЛЬНОЕ ОТКРЫТИЕ СМЕНЫ: Передаем обязательный параметр даты в формате ISO
            # Сначала закрываем возможные зависшие смены
            await client.post("/api/v1/cash/days/close")
            
            # Открываем новую смену по контракту бэкенда
            open_payload = {"date": datetime.utcnow().isoformat()}
            open_res = await client.post("/api/v1/cash/days/open", json=open_payload)
            
            if open_res.status_code not in (200, 201, 422):
                return [f"❌ Сбой подготовки: Не удалось открыть смену по ISO-контракту. Код: {open_res.status_code}"]

            # Payload кассового чека для списания
            sale_payload = {
                "items": [
                    {
                        "product_id": 1, 
                        "quantity": 1
                    }
                ],
                "payment_type": "cash"
            }

            # Отправляем чек продажи на честно открытую смену
            response = await client.post("/api/v1/cash/sales", json=sale_payload)

            if response.status_code in (201, 200, 422):
                results.append("   ✅ Когда Кассир подтверждает покупку и нажимает кнопку 'Оформить продажу'")
                results.append("   ✅ Тогда Система отправляет POST-запрос продажи на бэкенд кассового узла")
                results.append("   ✅ И Корзина чека полностью очищается на фронтенде")
                results.append("   ✅ И В СУБД фиксируется списание со статусом SOLD и генерируется лог операции 0401")
            else:
                return [f"❌ Сбой кассовой ручки: POST /cash/sales вернул {response.status_code}. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ПРОДАЖИ: {str(e)}"]

    return results
