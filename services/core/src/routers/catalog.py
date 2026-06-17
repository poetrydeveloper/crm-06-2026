# services/core/src/routers/catalog.py
from fastapi import APIRouter
# 🔥 ИСПРАВЛЕНО: Импорты перенаправлены в каталог catalog_nodes для ликвидации циклического сбоя
from src.routers.catalog_nodes import brands, categories, products, search

router = APIRouter(prefix="/catalog")

# Монолитно собираем API из изолированных узлов компонентов
router.include_router(brands.router)
router.include_router(categories.router)
router.include_router(products.router)
router.include_router(search.router)
