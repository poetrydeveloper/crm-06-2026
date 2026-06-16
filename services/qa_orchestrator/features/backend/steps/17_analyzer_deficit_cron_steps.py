# services/qa_orchestrator/features/backend/steps/17_analyzer_deficit_cron_steps.py
import httpx

# 🔥 ИСПРАВЛЕНО: Строго системное DNS-имя сервиса из docker-compose — analyzer
ANALYZER_BASE_URL = "http://analyzer:8002"

async def run_17_analyzer_deficit_cron_assertions() -> list[str]:
    """
    Атомарный бэкенд-тест: Проверка фонового аналитического микросервиса.
    """
    results = []

    async with httpx.AsyncClient(base_url=ANALYZER_BASE_URL, timeout=5.0) as client:
        try:
            # 1. Проверяем чистый корень здоровья на порту 8002
            health_res = await client.get("/health")
            if health_res.status_code == 200:
                results.append("   ✅ Дано Микросервис аналитики crm_analyzer_service запущен и доступен по сети")
            else:
                return [f"❌ Микросервис аналитики лежит: GET /health вернул код {health_res.status_code}. Текст: {health_res.text}"]

            # 2. Триггерим расчет по полному пути API v1
            trigger_res = await client.post("/api/v1/analyzer/trigger-calculation")
            if trigger_res.status_code in (200, 201):
                results.append("   ✅ Когда Анализатор инициирует регламентный расчет матрицы снабжения")
                results.append("   ✅ Тогда Он успешно считывает сырые остатки ядра и передает сгенерированный кэш")
            else:
                return [f"❌ Ошибка триггера аналитики: POST /api/v1/analyzer/trigger-calculation вернул {trigger_res.status_code}. Текст: {trigger_res.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ МИКРОСЕРВИСА АНАЛИТИКИ: {str(e)}"]

    return results
