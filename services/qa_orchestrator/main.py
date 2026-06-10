import os
import io
from fastapi import FastAPI, Response
from rich.console import Console
from rich.table import Table

from features.steps.catalog_steps import run_catalog_story_assertions
from features.steps.brand_steps import run_brand_lifecycle_and_transformations
from features.steps.category_steps import run_category_story_assertions
from features.steps.product_steps import run_product_story_assertions

app = FastAPI(title="CRM QA Orchestrator", version="1.0.0")

@app.post("/qa/run-stories")
async def run_all_stories():
    report = {
        "total": 0, "passed": 0, "failed": 0, "errors": []
    }
    
    stories = [
        ("01_Сквозной_поток_каталога", "features/catalog_flow.feature", run_catalog_story_assertions),
        ("02_Управление_брендами", "features/01_brand.feature", run_brand_lifecycle_and_transformations),
        ("03_Управление_категориями", "features/02_category.feature", run_category_story_assertions),
        ("04_Управление_товарами_и_аномалиями", "features/03_product.feature", run_product_story_assertions),
    ]

    for title, feature_path, assertion_fn in stories:
        if os.path.exists(feature_path):
            report["total"] += 1
            step_results = await assertion_fn()
            failed_steps = [step for step in step_results if "❌" in step]
            
            if failed_steps:
                report["failed"] += 1
                report["errors"].append({"story": title, "step": failed_steps[0]})
            else:
                report["passed"] += 1

    # РЕНДЕРИНГ КРАСИВОГО ВЫВОДА СИЛАМИ БИБЛИОТЕКИ RICH
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True, color_system="truecolor")
    
    # 1. Строим шапку с процентом выполнения
    rate = int((report["passed"] / report["total"]) * 100) if report["total"] > 0 else 0
    color = "green" if report["failed"] == 0 else "red"
    
    console.print(f"\n[bold white]📊 ОТЧЕТ QA-ОРКЕСТРАТОРА:[/bold white] [bold {color}]УСПЕШНОСТЬ {rate}%[/bold {color}] ({report['passed']}/{report['total']})\n")
    
    # 2. Строим компактную таблицу результатов
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("БИЗНЕС-ИСТОРИЯ", width=40)
    table.add_column("СТАТУС И КОНКРЕТНАЯ ОШИБКА", width=70)
    
    # Наполняем таблицу
    error_map = {err["story"]: err["step"] for err in report["errors"]}
    
    for title, feature_path, _ in stories:
        if os.path.exists(feature_path):
            if title in error_map:
                # Отрезаем значок крестика для чистоты и красим ошибку в красный
                clean_err = error_map[title].replace("❌ ", "")
                table.add_row(f"[red]• {title}[/red]", f"[bold red]❌ СБОЙ:[/bold red] [red]{clean_err}[/red]")
            else:
                table.add_row(f"[green]• {title}[/green]", "[bold green]✔ ПРОЙДЕН[/bold green]")
                
    console.print(table)
    console.print("\n" + "─"*115 + "\n")
    
    status_code = 400 if report["failed"] > 0 else 200
    return Response(content=string_io.getvalue(), media_type="text/plain; charset=utf-8", status_code=status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
