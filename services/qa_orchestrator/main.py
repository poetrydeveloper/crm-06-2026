# services/qa_orchestrator/main.py (ОБНОВЛЕННАЯ ЧАСТЬ 1 ИЗ 2)
import os
import io
import sys
import glob
import importlib
import httpx
import asyncpg
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import HTMLResponse
from rich.console import Console
from rich.table import Table

from utils.anomaly_checker import verify_core_routers

app = FastAPI(title="CRM Dynamic Multi-Scope QA Orchestrator", version="3.1.0")

DATABASE_URL = "postgresql://crm_admin:crm_secure_password@db:5432/crm_main_database"

# 📖 ЖИВАЯ ДОКУМЕНТАЦИЯ НА ГЛАВНОЙ СТРАНИЦЕ ОРКЕСТРАТОРА
@app.get("/", response_class=HTMLResponse)
async def get_orchestrator_manual():
    return """
    <html>
        <head><title>CRM QA Manual</title><style>body{font-family:monospace;padding:40px;background:#1e1e1e;color:#fff;}code{background:#333;padding:4px 8px;border-radius:4px;color:#ff79c6;}</style></head>
        <body>
            <h2>🚀 CRM QA-ОРКЕСТРАТОР: ШПАРГАЛКА КОМАНД ДЛЯ GIT BASH</h2>
            <hr>
            <p>🔥 <b>Проверить ВСЁ разом (Бэкенд + Фронтенд + Логи + Аналитика):</b><br>
            <code>curl -s -X POST http://localhost:8005/qa/run-stories/all</code></p>
            <p>📦 <b>Проверить только БЭКЕНД (15 историй FIFO и СУБД):</b><br>
            <code>curl -s -X POST http://localhost:8005/qa/run-stories/backend</code></p>
            <p>🎨 <b>Проверить только ФРОНТЕНД (Контракты UI Админки и Кассы):</b><br>
            <code>curl -s -X POST http://localhost:8005/qa/run-stories/frontend</code></p>
        </body>
    </html>
    """

async def global_clean_database():
    """Глобальная очистка СУБД перед стартом каждой бизнес-истории"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            TRUNCATE cash_event_items, cash_events, cash_days, 
                     product_units, products, categories, brands, suppliers 
            RESTART IDENTITY CASCADE;
        """)
        await conn.close()
    except Exception as e:
        print(f"⚠️ Ошибка очистки СУБД в оркестраторе: {e}", flush=True)

@app.post("/qa/run-stories/{scope}")
async def run_stories_by_scope(scope: str):
    """
    Динамический запуск BDD сценариев по плоскостям.
    При scope='all' автоматически сканирует и прогоняет ВСЕ существующие папки.
    """
    report = {"total": 0, "passed": 0, "failed": 0, "errors": []}
    table_rows = []
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True, color_system="truecolor")

    # Базовая проверка здоровья инфраструктуры перед тестами
    is_routers_healthy, anomaly_error = await verify_core_routers()
    if not is_routers_healthy:
        report["total"] = 1
        report["failed"] = 1
        report["errors"].append({"story": "КРИТИЧЕСКИЙ БЛОКЕР ИНФРАСТРУКТУРЫ", "step": anomaly_error})
        table_rows.append(("КРИТИЧЕСКИЙ БЛОКЕР ИНФРАСТРУКТУРЫ", "red", f"❌ ЗАБЛОКИРОВАНО: {anomaly_error}"))
        return await generate_rich_response(report, table_rows, string_io, console)

    # УНИВЕРСАЛЬНЫЙ СБОР ФАЙЛОВ СЦЕНАРИЕВ
    feature_files = []
    scope_param = scope.lower().strip()

    if scope_param == "all":
        # Если вызван 'all' — собираем абсолютно все фичи из всех подпапок в features/
        feature_files = sorted(glob.glob("features/**/*.feature", recursive=True))
    else:
        clean_scope = os.path.basename(scope_param)
        scope_dir = f"features/{clean_scope}"
        if not os.path.exists(scope_dir):
            raise HTTPException(status_code=404, detail=f"Зона тестирования '{clean_scope}' не найдена. Создайте папку {scope_dir}")
        feature_files = sorted(glob.glob(f"{scope_dir}/[0-9][0-9]_*.feature"))

    if not feature_files:
        return Response(content=f"Сценарии .feature в выбранной зоне '{scope_param}' отсутствуют.\n", media_type="text/plain")
# services/qa_orchestrator/main.py (ОБНОВЛЕННАЯ ЧАСТЬ 2 ИЗ 2)
    for feature_path in feature_files:
        # Принцип чистого листа: зачищаем базу перед каждым сценарием
        await global_clean_database()

        report["total"] += 1
        filename = os.path.basename(feature_path)
        prefix = filename[:2]
        
        # Динамически вычисляем директорию фичи (работает и для конкретного scope, и для 'all')
        current_scope_dir = os.path.dirname(feature_path)
        
        # Находим файл шагов по префиксу внутри правильного каталога
        steps_pattern = f"{current_scope_dir}/steps/{prefix}_*_steps.py"
        steps_files = glob.glob(steps_pattern)
        
        if not steps_files:
            table_rows.append((filename, "red", f"❌ ПРОПУЩЕН: Нет файла шагов {prefix}"))
            report["failed"] += 1
            report["errors"].append({"story": filename, "step": f"Отсутствует файл реализации шагов в {current_scope_dir}/steps/"})
            continue  # Безопасно переходим к СЛЕДУЮЩЕЙ фиче
            
        steps_file = steps_files[0]
        # Безопасно преобразуем путь в имя модуля (заменяем слэши на точки)
        module_name = steps_file.replace("/", ".").replace("\\", ".").replace(".py", "")
        
        try:
            # Очищаем кэш импорта, чтобы изменения в тестах подтягивались на лету
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            module = importlib.import_module(module_name)
            
            assertion_fn = None
            for attr in dir(module):
                if attr.startswith("run_") and attr.endswith("_assertions"):
                    assertion_fn = getattr(module, attr)
                    break
                    
            if not assertion_fn:
                raise Exception(f"В модуле {module_name} не найдена функция run_*_assertions")

            step_results = await assertion_fn()
            failed_steps = [step for step in step_results if "❌" in step]
            
            if failed_steps:
                report["failed"] += 1
                clean_err = failed_steps[0].replace("❌ ", "")
                report["errors"].append({"story": filename, "step": clean_err})
                table_rows.append((filename, "red", f"❌ СБОЙ: {clean_err}"))
            else:
                report["passed"] += 1
                table_rows.append((filename, "green", "✔ ПРОЙДЕН"))
                
        except Exception as e:
            report["failed"] += 1
            report["errors"].append({"story": filename, "step": str(e)})
            table_rows.append((filename, "red", f"❌ АВАРЕЙНЫЙ СБОЙ: {str(e)}"))

    return await generate_rich_response(report, table_rows, string_io, console)


async def generate_rich_response(report, table_rows, string_io, console):
    rate = int((report["passed"] / report["total"]) * 100) if report["total"] > 0 else 0
    color = "green" if report["failed"] == 0 else "red"
    
    console.print(f"\n[bold white]📊 МУЛЬТИЗОНАЛЬНЫЙ ОТЧЕТ QA-ОРКЕСТРАТОРА:[/bold white] [bold {color}]УСПЕШНОСТЬ {rate}%[/bold {color}] ({report['passed']}/{report['total']})\n")
    
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("БИЗНЕС-ИСТОРИЯ (ДИНАМИЧЕСКИЙ ПОИСК)")
    table.add_column("СТАТУС И ДЕТАЛИЗАЦИЯ")
    
    for filename, text_color, status_text in table_rows:
        table.add_row(f"[{text_color}]• {filename}[/{text_color}]", f"[{text_color}]{status_text}[/{text_color}]")
        
    console.print(table)
    
    if report["errors"]:
        console.print("\n[bold yellow]🔍 ДЕТАЛИЗАЦИЯ КРИТИЧЕСКИХ ОШИБОК ДЛЯ ОТЛАДКИ:[/bold yellow]")
        for err in report["errors"]:
            console.print(f"[red]• История:[/red] [white]{err['story']}[/white]")
            console.print(f"  [red]Сбой на шаге:[/red] [bold yellow]{err['step']}[/bold yellow]\n")
            
            if "11_cashbox_smart_search" in err['story']:
                console.print("[bold cyan]📊 [ОТЧЕТ ИЗ БАЗЫ ДАННЫХ ДЛЯ ОРАКЛА]:[/bold cyan]")
                try:
                    async with httpx.AsyncClient() as client:
                        db_snap = await client.get("http://backend:8000/api/v1/catalog/debug-db-raw-product", timeout=2.0)
                        if db_snap.status_code == 200:
                            raw = db_snap.json()
                            console.print(f"   ▪️ [Имя товара в БД]: [green]{raw.get('name')}[/green]")
                            console.print(f"   ▪️ [Код / Артикул]:   [green]{raw.get('code')}[/green]")
                            console.print(f"   ▪️ [Массив тегов]:    [magenta]{raw.get('search_tags_value')}[/magenta]")
                            console.print(f"   ▪️ [Массив алиасов]:  [magenta]{raw.get('search_aliases_value')}[/magenta]\n")
                except Exception:
                    pass
            
    console.print("─"*100 + "\n")
    status_code = 400 if report["failed"] > 0 else 200
    return Response(content=string_io.getvalue(), media_type="text/plain; charset=utf-8", status_code=status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
