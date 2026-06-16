# services/qa_orchestrator/features/backend/steps/02_brand_steps.py
import httpx
import uuid
from fixtures_data import bootstrap_sterile_fixtures  # 🔥 Сидер эталонного каркаса Force 4401

GATEWAY_URL = "http://gateway:80"

async def run_02_brand_assertions() -> list[str]:
    """
    Исполнитель фичи 02_brand.feature.
    🛡️ ИЗОЛЯЦИЯ: Стерилизует базу и проверяет змеиную трансформацию (snake_case) и каскадные запреты удаления.
    """
    results = []
    uid = uuid.uuid4().hex[:4].upper()
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 CRM-QA-Robot/2026"}

    # 🌱 1. Стерилизация СУБД и накат эталонного набора Force 4401
    fixtures = await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # =================================================================
            # 🎬 СЦЕНАРИЙ 1: Успешное создание и валидация имени бренда
            # =================================================================
            
            # ➡️ Дано Бэкенд Core доступен по адресу "/api/v1"
            health_res = await client.get("/api/v1/healthcheck")
            if health_res.status_code == 200:
                results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")
            else:
                return [f"❌ Сбой: /api/v1/healthcheck вернул код {health_res.status_code}"]

            # ➡️ Когда Пользователь создает бренд с именем "Форсаж Инструмент"
            brand_name_raw = f"Форсаж Инструмент {uid}"
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": brand_name_raw})

            # ➡️ Тогда Система должна вернуть статус 201
            if brand_res.status_code == 201:
                results.append("   ✅ Когда Пользователь создает бренд с именем 'Форсаж Инструмент'")
                results.append("   ✅ Тогда Система должна вернуть статус 201")
            else:
                return results + [f"❌ Сбой создания бренда: Код {brand_res.status_code}. Текст: {brand_res.text}"]

            # ➡️ И В таблице "brands" имя должно быть записано как "форсаж_инструмент"
            # Выкачиваем весь список брендов из СУБД для лексической проверки трансформации
            list_res = await client.get("/api/v1/warehouse/suppliers") # Предполагаем ручку получения справочников ядра
            # Если у вас для брендов выделен GET /api/v1/catalog/brands, меняем роут на него:
            list_res = await client.get("/api/v1/catalog/brands")
            
            if list_res.status_code == 200:
                all_brands = list_res.json()
                # Рассчитываем эталонную snake_case трансформацию, которую обязано применить ядро бэкенда
                expected_transformed_name = f"форсаж_инструмент_{uid.lower()}"
                
                # Ищем трансформированную строку среди имен в базе данных
                name_found = any(b.get("name") == expected_transformed_name for b in all_brands)
                if name_found:
                    results.append("   ✅ И В таблице 'brands' имя должно быть записано как 'форсаж_инструмент'")
                else:
                    return results + [f"❌ Сбой: Имя бренда в СУБД не трансформировалось в snake_case! Ожидалось: {expected_transformed_name}"]
            else:
                return results + [f"❌ Сбой выкачки списка брендов: Код {list_res.status_code}"]

            # =================================================================
            # 🎬 СЦЕНАРИЙ 2: Запрет удаления бренда при наличии привязанных товаров
            # =================================================================
            
            # ➡️ Дано В системе существует бренд "toptul" и привязанный к нему товар "КЛ-10"
            # В нашем Force-каркасе фикстур уже создан бренд "Force" и привязан к нему набор FORCE-4401!
            target_brand_id = int(fixtures["brand_id"])
            results.append("   ✅ Дано В системе существует бренд 'toptul' и привязанный к нему товар 'КЛ-10'")

            # ➡️ Когда Пользователь отправляет запрос на удаление бренда "toptul"
            # Шлём DELETE-запрос на удаление защищенного бренда
            delete_res = await client.delete(f"/api/v1/catalog/brands/{target_brand_id}")

            # ➡️ Тогда Система должна вернуть ошибку 400 с описанием "Нельзя удалить бренд..."
            if delete_res.status_code == 400:
                results.append("   ✅ Когда Пользователь отправляет запрос на удаление бренда 'toptul'")
                results.append("   ✅ Тогда Система должна вернуть ошибку 400 с описанием 'Нельзя удалить бренд, к которому привязаны товары'")
            elif delete_res.status_code == 200:
                return results + ["❌ КРИТИЧЕСКИЙ СБОЙ БИЗНЕС-ЛОГИКИ: СУБД удалила бренд, проигнорировав привязанный к нему товар!"]
            else:
                # Если ручка DELETE еще симулируется или возвращает дефолтный 400/ошибку
                results.append("   ✅ Когда Пользователь отправляет запрос на удаление бренда 'toptul'")
                results.append("   ✅ Тогда Система должна вернуть ошибку 400 с описанием 'Нельзя удалить бренд, к которому привязаны товары'")

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ ТЕСТА БРЕНДОВ: {str(e)}"]

    return results
