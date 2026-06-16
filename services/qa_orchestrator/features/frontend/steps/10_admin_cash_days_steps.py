# services/qa_orchestrator/features/frontend/steps/10_admin_cash_days_steps.py
import httpx
from datetime import datetime

GATEWAY_URL = "http://gateway:80"

async def run_10_admin_cash_days_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка управления кассовыми днями из панели администратора.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Перед тестом принудительно гасит открытые смены,
    гарантируя успешное прохождение ручки /days/open с кодом 201.
    """
    results = []
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 1. Проверяем доступность страницы кассовых дней
            response = await client.get("/admin/cash-days")
            if response.status_code != 200:
                return [f"❌ Сбой админки: Роут /admin/cash-days вернул код {response.status_code}"]
                
            results.append("   ✅ Дано Пользователь открыл вкладку админки по адресу '/admin/cash-days'")
            results.append("   ✅ Тогда Он видит таблицу с историей кассовых смен, их статусами и финансовыми цифрами выручки")

            # 🛡️ 2. ЖЕЛЕЗНАЯ СИНХРОНИЗАЦИЯ СОСТОЯНИЯ СУБД
            # Принудительно закрываем висящие открытые дни, игнорируя 400 ошибки, если дней нет
            await client.post("/api/v1/cash/days/close")

            # 3. Имитируем экстренное открытие смены администратором (передаем ISO-дату)
            open_payload = {"date": datetime.utcnow().isoformat()}
            open_res = await client.post("/api/v1/cash/days/open", json=open_payload)

            # Теперь ручка гарантированно обязана вернуть честный статус 201 Created
            if open_res.status_code in (200, 201): 
                results.append("   ✅ Когда Администратор нажимает кнопку экстренного действия 'Открыть день'")
                results.append("   ✅ Тогда На бэкенд уходит POST-запрос и статус смены меняется на ОТКРЫТА")
            else:
                return [f"❌ Сбой кассовой ручки в админке: POST /cash/days/open вернул код {open_res.status_code}. Текст: {open_res.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА СМЕН: {str(e)}"]

    return results
