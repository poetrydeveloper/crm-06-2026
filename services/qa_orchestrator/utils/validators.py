# services/qa_orchestrator/utils/validators.py
import urllib.parse

def validate_jsonb_tags(tags_list: list, expected: list, excluded: list) -> tuple[bool, str]:
    """Универсальный компонент для валидации поисковых тегов карточки товара"""
    # Переводим всё в нижний регистр для безопасного сравнения
    clean_tags = [str(t).lower().strip() for t in tags_list]
    
    # 1. Проверяем обязательное наличие тегов
    for exp in expected:
        if exp.lower().strip() not in clean_tags:
            return False, f"В JSONB отсутствуют ожидаемый тег '{exp}'. Текущий массив: {clean_tags}"
            
    # 2. Проверяем строгое отсутствие стоп-слов (предлогов и мусора)
    for excl in excluded:
        if excl.lower().strip() in clean_tags:
            return False, f"Критическая ошибка очистки: стоп-слово '{excl}' просочилось в СУБД!"
            
    return True, ""

def safe_header(text: str) -> str:
    """Экранирует кириллицу для безопасной передачи в HTTP-заголовках"""
    return urllib.parse.quote(text)