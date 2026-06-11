# services/qa_orchestrator/utils/extract_routes.py
import httpx
import json

CORE_OPENAPI_URL = "http://crm_backend_core:8000/openapi.json"
OUTPUT_FILE = "core_routes_map.txt"

def build_routes_map():
    print("⏳ Подключение к ядру для выгрузки карты роутеров...")
    try:
        response = httpx.get(CORE_OPENAPI_URL, timeout=5.0)
        if response.status_code != 200:
            print(f"❌ Ошибка. Бэкенд вернул статус {response.status_code}")
            return
            
        data = response.json()
        paths = data.get("paths", {})
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("========================================================================\n")
            f.write("🗺️  ПОЛНАЯ КАРТА ЭНДПОИНТОВ И РОУТЕРОВ CORE-БЭКЕНДА (АВТОГЕНЕРАЦИЯ)\n")
            f.write("========================================================================\n\n")
            
            for path, methods in sorted(paths.items()):
                f.write(f"🛣️  ПУТЬ (ROUTE): {path}\n")
                f.write("-" * 60 + "\n")
                
                for method, details in methods.items():
                    method_upper = method.upper()
                    summary = details.get("summary", "Описание отсутствует")
                    operation_id = details.get("operationId", "Не указан")
                    tags = ", ".join(details.get("tags", []))
                    
                    f.write(f"  ▪️ [МЕТОД]:       {method_upper}\n")
                    f.write(f"  ▪️ [ЧТО ДЕЛАЕТ]:   {summary}\n")
                    f.write(f"  ▪️ [ФУНКЦИЯ КОДА]: {operation_id}\n")
                    f.write(f"  ▪️ [ТЕГИ/ГРУППА]:  {tags}\n")
                    
                    # Проверяем возможные ответы (status codes)
                    responses = details.get("responses", {})
                    codes = ", ".join(responses.keys())
                    f.write(f"  ▪️ [КОДЫ ОТВЕТОВ]: {codes}\n")
                    f.write("\n")
                f.write("=" * 80 + "\n\n")
                
        print(f"✅ Успех! Карта роутеров сохранена в файл: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ Не удалось собрать роуты: {e}")

if __name__ == "__main__":
    build_routes_map()
