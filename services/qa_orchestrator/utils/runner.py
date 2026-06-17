# services/qa_orchestrator/utils/runner.py
import sys
import importlib

async def execute_steps_file(steps_file_path: str) -> list[str]:
    """Безопасно импортирует файл шагов и запускает асинхронные проверки"""
    # Превращаем путь в системный импорт
    module_name = steps_file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
    
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
        
    module = importlib.import_module(module_name)
    
    # Ищем функцию-исполнитель контракта
    assertion_fn = None
    for attr in dir(module):
        if attr.startswith("run_") and attr.endswith("_assertions"):
            assertion_fn = getattr(module, attr)
            break
            
    if not assertion_fn:
        raise Exception(f"В модуле {module_name} не найдена функция run_*_assertions")
        
    return await assertion_fn()
