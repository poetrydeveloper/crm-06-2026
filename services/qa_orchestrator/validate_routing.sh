#!/bin/bash
# Скрипт автоматического аудита точек входа и маршрутов FastAPI

echo "🔍 Запуск автоматического аудита инфраструктуры бэкенда..."
echo "--------------------------------------------------------"

# 1. Проверяем, какой именно файл main.py запускается внутри докера
echo "1. Проверка рабочей точки входа Uvicorn:"
UVICORN_CMD=$(docker compose exec backend ps -ef | grep uvicorn | grep -v grep)
echo "   Живой процесс в контейнере: $UVICORN_CMD"

# 2. Физический поиск дубликатов main.py
echo -e "\n2. Поиск дублирующих файлов main.py в контейнере:"
docker compose exec backend find /app -name "main.py"

# 3. Выгрузка РЕАЛЬНОЙ карты роутов из памяти работающего процесса
echo -e "\n3. Выгрузка активных роутов из оперативной памяти FastAPI:"
docker compose exec backend python -c "
try:
    import sys
    sys.path.append('/app')
    # Пробуем загрузить модуль так же, как его загружает Uvicorn в Dockerfile
    import main
    if hasattr(main, 'app'):
        print('\n'.join([f'   --> [{list(r.methods)}] {r.path}' for r in main.app.routes if hasattr(r, 'path')]))
    else:
        print('   ❌ Ошибка: В корневом файле main.py не найден объект app!')
except Exception as e:
    print('   ❌ Критическая ошибка импорта при старте корня:', str(e))
"

echo "--------------------------------------------------------"
echo "💡 Сравните список роутов выше с адресами ваших тестов. Если нужного роута тут нет — он не зарегистрирован в main.py!"
