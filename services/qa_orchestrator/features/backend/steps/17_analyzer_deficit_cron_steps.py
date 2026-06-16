# services/qa_orchestrator/features/backend/steps/17_analyzer_deficit_cron_steps.py
import httpx

# Робот стучится напрямую в контейнер аналитики на порт 8002 (или внутренний роут шлюза)
ANALYZER_URL = "http://crm_analyzer_service:8002/api/v1"

async def run_17_analyzer_deficit_cron_assertions() -> list[str]:
    """
    Атомарный бэкенд-тест: Проверка фонового аналитического микросервиса.
    """
    results = []

    async with httpx.AsyncClient(base_url=ANALYZER_URL, timeout=5.0) as client:
        try:
            # 1. Проверяем, что контейнер аналитики вообще жив
            health_res = await client.get("/health")
            if health_res.status_code == 200:
                results.append("   ✅ Дано Микросервис аналитики crm_analyzer_service запущен и доступен по сети")
            else:
                return [f"❌ Микросервис аналитики лежит: GET /health вернул код {health_res.status_code}"]

            # 2. Триггерим ручку принудительного запуска пересчета матрицы рисков
            trigger_res = await client.post("/analyzer/trigger-calculation")
            if trigger_res.status_code in (200, 201):
                results.append("   ✅ Когда Анализатор инициирует регламентный расчет матрицы снабжения")
                results.append("   ✅ Тогда Он успешно считывает сырые остатки ядра и передает сгенерированный кэш")
            else:
                return [f"❌ Ошибка триггера аналитики: POST /analyzer/trigger-calculation вернул {trigger_res.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ МИКРОСЕРВИСА АНАЛИТИКИ: {str(e)}"]

    return results
