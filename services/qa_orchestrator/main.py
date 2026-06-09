import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from features.steps.catalog_steps import run_catalog_story_assertions

app = FastAPI(
    title="CRM QA Orchestrator",
    description="Микросервис автоматического контроля бизнес-сценариев и регрессии",
    version="1.0.0"
)

@app.get("/qa/health")
async def qa_health():
    """Проверка доступности самого тестового оркестратора"""
    return {"status": "online", "service": "qa_orchestrator"}

@app.post("/qa/run-stories")
async def run_all_stories():
    """
    Эндпоинт запуска сквозного тестирования пользовательских историй.
    Сканирует папку features и поочередно запускает логику проверок.
    """
    report = {
        "execution_status": "completed",
        "total_stories_checked": 0,
        "failed_stories": 0,
        "details": {}
    }
    
    # --- 1. ПРОВЕРКА ИСТОРИИ: catalog_flow.feature ---
    feature_path = "features/catalog_flow.feature"
    if os.path.exists(feature_path):
        report["total_stories_checked"] += 1
        
        # Читаем текст фичи, чтобы прикрепить его к отчету для наглядности
        with open(feature_path, "r", encoding="utf-8") as f:
            feature_text = f.read()
            
        # Запускаем асинхронный движок шагов
        step_results = await run_catalog_story_assertions()
        
        # Проверяем, были ли сбои среди шагов этой истории
        has_failed_steps = any("❌" in result for result in step_results)
        
        if has_failed_steps:
            report["failed_stories"] += 1
            status = "FAILED"
        else:
            status = "PASSED"
            
        report["details"]["Наполнение каталога и автогенерация тегов"] = {
            "status": status,
            "feature_file": feature_path,
            "steps_report": step_results
        }
    else:
        report["details"]["Каталог"] = {"status": "SKIPPED", "reason": f"Файл {feature_path} не найден"}

    # Если хотя бы одна глобальная история завалилась — отдаем статус 400 (Bad Request),
    # чтобы CI/CD или скрипты деплоя сразу поняли, что код сломан.
    if report["failed_stories"] > 0:
        return JSONResponse(status_code=400, content=report)
        
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)