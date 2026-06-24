# services/qa_orchestrator/main.py
import os
import io
import glob
import asyncio
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import HTMLResponse
from rich.console import Console
from rich.table import Table

from utils.anomaly_checker import verify_core_routers
from utils.runner import execute_steps_file  # Наш новый компонент!

app = FastAPI(title="CRM Dynamic Multi-Scope QA Orchestrator", version="3.1.0")

# 🔥 ИСПРАВЛЕНО: Префикс изменен на postgres://, так как asyncpg рухнет на postgresql://
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgres://crm_admin:crm_secure_password@db:5432/crm_main_database"
)
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgres://")
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://")


@app.get("/", response_class=HTMLResponse)
async def get_orchestrator_manual():
    return """
    <html>
        <head><title>CRM QA Manual</title><style>body{font-family:monospace;padding:40px;background:#1e1e1e;color:#fff;}code{background:#333;padding:4px 8px;border-radius:4px;color:#ff79c6;}</style></head>
        <body>
            <h2>🚀 CRM QA-ОРКЕСТРАТОР: ШПАРГАЛКА КОМАНД</h2>
            <hr>
            <p>🔥 <b>Проверить ВСЁ разом:</b><br><code>curl -s -X POST http://localhost:8005/qa/run-stories/all</code></p>
        </body>
    </html>
    """


async def global_clean_database():
    import asyncpg

    try:
        conn = await asyncpg.connect(DATABASE_URL)
        # 🔥 ИСПРАВЛЕНО: Каскадно чистим таблицы, но мгновенно возвращаем Системного поставщика
        # с текущими датами NOW(), чтобы не ломать фронтенд CRM-системы после прогона тестов
        await conn.execute("""
            TRUNCATE cash_event_items, cash_events, cash_days, 
                     product_units, products, categories, brands, suppliers 
            RESTART IDENTITY CASCADE;
            
            INSERT INTO suppliers (id, name, created_at, updated_at) 
            VALUES (1, 'Системный поставщик', NOW(), NOW()) 
            ON CONFLICT (name) DO NOTHING;
        """)
        await conn.close()
    except Exception as e:
        print(f"⚠️ Ошибка очистки СУБД в оркестраторе: {e}", flush=True)


@app.post("/qa/run-stories/{scope}")
async def run_stories_by_scope(scope: str):
    report = {"total": 0, "passed": 0, "failed": 0, "errors": []}
    table_rows = []
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True, color_system="truecolor")

    is_routers_healthy, anomaly_error = await verify_core_routers()
    if not is_routers_healthy:
        report.update({"total": 1, "failed": 1})
        report["errors"].append(
            {"story": "КРИТИЧЕСКИЙ БЛОКЕР ИНФРАСТРУКТУРЫ", "step": anomaly_error}
        )
        table_rows.append(
            (
                "КРИТИЧЕСКИЙ БЛОКЕР ИНФРАСТРУКТУРЫ",
                "red",
                f"❌ ЗАБЛОКИРОВАНО: {anomaly_error}",
            )
        )
        return await generate_rich_response(report, table_rows, string_io, console)
    scope_param = scope.lower().strip()
    if scope_param == "all":
        feature_files = sorted(glob.glob("features/**/*.feature", recursive=True))
    else:
        clean_scope = os.path.basename(scope_param)
        scope_dir = f"features/{clean_scope}"
        if not os.path.exists(scope_dir):
            raise HTTPException(
                status_code=404, detail=f"Зона тестирования '{clean_scope}' не найдена."
            )
        feature_files = sorted(glob.glob(f"{scope_dir}/[0-9][0-9]_*.feature"))

    if not feature_files:
        return Response(
            content=f"Сценарии in выбранной зоне '{scope_param}' отсутствуют.\n",
            media_type="text/plain",
        )

    for feature_path in feature_files:
        await global_clean_database()
        report["total"] += 1
        filename = os.path.basename(feature_path)
        prefix = filename[:2]

        current_scope_dir = os.path.dirname(feature_path)
        steps_files = glob.glob(f"{current_scope_dir}/steps/{prefix}_*_steps.py")

        if not steps_files:
            table_rows.append(
                (filename, "red", f"❌ ПРОПУЩЕН: Нет файла шагов {prefix}")
            )
            report["failed"] += 1
            report["errors"].append(
                {"story": filename, "step": "Отсутствует файл реализации шагов"}
            )
            continue

        try:
            # 🔥 ИСПРАВЛЕНО: Добавлен вывод живого лога перед запуском файла шагов
            print(
                f"⏳ [QA RUNNER]: Запуск сценария {filename} с шагами {os.path.basename(steps_files[0])}...",
                flush=True,
            )

            # 🔥 ИСПРАВЛЕНО: Обернули выполнение в асинхронный таймаут, защищая Event Loop от зависания
            try:
                step_results = await asyncio.wait_for(
                    execute_steps_file(steps_files[0]), timeout=7.0
                )
            except asyncio.TimeoutError:
                raise Exception(
                    "Превышен лимит времени сценария (Таймаут 7 секунд). Проверьте шаги на бесконечные циклы."
                )

            failed_steps = [step for step in step_results if "❌" in step]

            if failed_steps:
                report["failed"] += 1
                report["errors"].append(
                    {"story": filename, "step": failed_steps[0].replace("❌ ", "")}
                )
                table_rows.append((filename, "red", f"❌ СБОЙ"))
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
    console.print(
        f"\n[bold white]📊 МУЛЬТИЗОНАЛЬНЫЙ ОТЧЕТ QA-ОРКЕСТРАТОРА:[/bold white] [bold {color}]УСПЕШНОСТЬ {rate}%[/bold {color}] ({report['passed']}/{report['total']})\n"
    )

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("БИЗНЕС-ИСТОРИЯ (ДИНАМИЧЕСКИЙ ПОИСК)")
    table.add_column("СТАТУС И ДЕТАЛИЗАЦИЯ")
    for fn, t_color, status in table_rows:
        table.add_row(
            f"[{t_color}]• {fn}[/{t_color}]", f"[{t_color}]{status}[/{t_color}]"
        )
    console.print(table)

    if report["errors"]:
        console.print(
            "\n[bold yellow]🔍 ДЕТАЛИЗАЦИЯ КРИТИЧЕСКИХ ОШИБОК ДЛЯ ОТЛАДКИ:[/bold yellow]"
        )
        for err in report["errors"]:
            console.print(
                f"[red]• История:[/red] {err['story']}\n  [red]Сбой на шаге:[/red] [bold yellow]{err['step']}[/bold yellow]\n"
            )
    console.print("─" * 100 + "\n")
    return Response(
        content=string_io.getvalue(),
        media_type="text/plain; charset=utf-8",
        status_code=400 if report["failed"] > 0 else 200,
    )
