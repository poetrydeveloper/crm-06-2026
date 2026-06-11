# services/qa_orchestrator/utils/anomaly_checker.py
import httpx

# Адрес ядра внутри Docker-сети
CORE_OPENAPI_URL = "http://crm_backend_core:8000/openapi.json"

async def verify_core_routers():
    """
    Сканирует OpenAPI схему ядра и проверяет роутеры на наличие аномалий версионирования.
    Возвращает (True, None), если все отлично.
    Возвращает (False, "текст ошибки"), если обнаружена аномалия.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(CORE_OPENAPI_URL, timeout=5.0)
            
        if response.status_code != 200:
            return False, f"Не удалось получить схему OpenAPI. Статус: {response.status_code}"
            
        data = response.json()
        paths = data.get("paths", {})
        
        if not paths:
            return False, "Схема OpenAPI пуста. Роутеры ядра не обнаружены."

        # Сканируем пути на наличие аномалий
        for path in paths.keys():
            # Аномалия №1: Роутер забыл обязательный префикс /api/v1
            if not path.startswith("/api/v1/"):
                return False, f"🚨 АНОМАЛИЯ РОУТИНГА: Эндпоинт '{path}' нарушает стандарт версионирования и пропустил префикс /api/v1!"
            
            # Аномалия №2: Проверка на системные хелсчеки (код 0000), если роутер тестовый ушел в прод
            if "test" in path.lower() and not path.startswith("/api/v1/qa"):
                return False, f"🚨 АНОМАЛИЯ БЕЗОПАСНОСТИ: Обнаружен сырой тестовый роутер '{path}' в ядре!"

        return True, None

    except httpx.RequestError as exc:
        return False, f"Ядро crm_backend_core недоступно по сети: {exc}"
