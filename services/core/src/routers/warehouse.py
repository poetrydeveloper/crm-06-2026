# services/core/src/routers/warehouse.py
from fastapi import APIRouter
# 🔥 ИСПРАВЛЕНО: Импортируем из чистой папки узлов без файловых конфликтов
from src.routers.warehouse_nodes import orders, pre_orders, operations, rules

router = APIRouter(prefix="/warehouse")

# Монолитно склеиваем складские роуты из наших изолированных файлов-компонентов
router.include_router(orders.router)
router.include_router(pre_orders.router)
router.include_router(operations.router)
router.include_router(rules.router)
