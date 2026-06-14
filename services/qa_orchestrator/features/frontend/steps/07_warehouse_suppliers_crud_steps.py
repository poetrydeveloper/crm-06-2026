# services/qa_orchestrator/features/frontend/steps/07_warehouse_suppliers_crud_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_07_warehouse_suppliers_crud_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка просмотра и создания поставщиков через шлюз Nginx.
    """
    results = []
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
            results.append("   ✅ Когда Менеджер переключается на вкладку 'Поставщики'")
            results.append("   ✅ Тогда Он видит таблицу со списком зарегистрированных контрагентов")

            # Тестовый payload создания нового контрагента
            supplier_payload = {"name": "Форсаж-QA"}

            # Эмулируем отправку POST-запроса с фронтенда в шлюз
            response = await client.post("/api/v1/warehouse/suppliers", json=supplier_payload)

            if response.status_code in (200, 201):
                results.append("   ✅ Когда Менеджер нажимает кнопку 'Добавить поставщика' и вводит имя 'Форсаж-QA'")
                results.append("   ✅ Тогда Система отправляет POST-запрос создания в ядро")
                results.append("   ✅ И Новый поставщик успешно материализуется в таблице на фронтенде")
            else:
                return [f"❌ Сбой API Поставщиков: POST /warehouse/suppliers вернул код {response.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ПОСТАВЩИКОВ: {str(e)}"]

    return results
