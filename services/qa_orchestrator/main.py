import os
import io
import glob
import importlib
from fastapi import FastAPI, Response
from rich.console import Console
from rich.table import Table

# ИСПРАВЛЕНО: Все жесткие импорты удалены. Теперь движок на 100% автономен и динамичен!
app = FastAPI(title="CRM Dynamic QA Orchestrator", version="2.0.0")

@app.post("/qa/run-stories")
async def run_all_stories():
    report = {"total": 0, "passed": 0, "failed": 0, "errors": []}
    feature_files = sorted(glob.glob("features/[0-9][0-9]_*.feature"))
    table_rows = []

    for feature_path in feature_files:
        report["total"] += 1
        filename = os.path.basename(feature_path)
        prefix = filename[:2]
        
        steps_pattern = f"features/steps/{prefix}_*_steps.py"
        steps_files = glob.glob(steps_pattern)
        
        if not steps_files:
            table_rows.append((filename, "red", f"❌ ПРОПУЩЕН: Нет файла шагов {prefix}"))
            report["failed"] += 1
            report["errors"].append({"story": filename, "step": "Отсутствует файл реализации шагов"})
            continue
            
        steps_file = steps_files[0]
        module_name = steps_file.replace("/", ".").replace(".py", "")
        
        try:
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

    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True, color_system="truecolor")
    
    rate = int((report["passed"] / report["total"]) * 100) if report["total"] > 0 else 0
    color = "green" if report["failed"] == 0 else "red"
    
    console.print(f"\n[bold white]📊 ДИНАМИЧЕСКИЙ ОТЧЕТ QA-ОРКЕСТРАТОРА:[/bold white] [bold {color}]УСПЕШНОСТЬ {rate}%[/bold {color}] ({report['passed']}/{report['total']})\n")
    
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("БИЗНЕС-ИСТОРИЯ (АВТОПОИСК)")
    table.add_column("СТАТУС И ДЕТАЛИЗАЦИЯ")
    
    for filename, text_color, status_text in table_rows:
        table.add_row(f"[{text_color}]• {filename}[/{text_color}]", f"[{text_color}]{status_text}[/{text_color}]")
        
    console.print(table)
    
    if report["errors"]:
        console.print("\n[bold yellow]🔍 ДЕТАЛИЗАЦИЯ КРИТИЧЕСКИХ ОШИБОК ДЛЯ ОТЛАДКИ:[/bold yellow]")
        for err in report["errors"]:
            console.print(f"[red]• История:[/red] [white]{err['story']}[/white]")
            console.print(f"  [red]Сбой на шаге:[/red] [bold yellow]{err['step']}[/bold yellow]\n")
            
    console.print("─"*100 + "\n")
    
    status_code = 400 if report["failed"] > 0 else 200
    return Response(content=string_io.getvalue(), media_type="text/plain; charset=utf-8", status_code=status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
