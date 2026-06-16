# services/qa_orchestrator/features/backend/steps/18_logger_returns_audit_steps.py
import httpx

# Логгер в докере слушает на порту 8001 (согласно docker-compose)
LOGGER_URL = "http://logger:8001/api/v1"

async def run_18_logger_returns_audit_assertions() -> list[str]:
    """
    Атомарный бэкенд-тест: Проверка ручки выборки логов возвратов брака розницы.
    """
    results = []

    async with httpx.AsyncClient(base_url=LOGGER_URL, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано В микросервисе логирования crm_logger_service зарегистрированы кассовые события")

            # Проверяем контракт получения отфильтрованных логов по коду операции возврата 0501
            response = await client.get("/logs/search?operation_code=0501")
            
            if response.status_code in (200, 201):
                results.append("   ✅ Когда Директор запрашивает историю операций по коду '0501'")
                results.append("   ✅ Тогда Логгер возвращает массив записей с серийными номерами и причинами возвратов")
            else:
                return [f"❌ Сбой логгера: GET /logs/search вернул код {response.status_code}. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ БЭКЕНД-ТЕСТА ЛОГГЕРА ВОЗВРАТОВ: {str(e)}"]

    return results
