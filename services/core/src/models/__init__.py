# services/core/src/models/__init__.py
from .base import Base
from .brand import Brand
from .category import Category
from .product import Product
from .supplier import Supplier
from .product_unit import ProductUnit, LogisticsStatus, PhysicalStatus
from .customer import Customer
from .cash_day import CashDay
from .cash_event import CashEvent, CashEventType
from .cash_event_item import CashEventItem
from .pending_sale import PendingSale
from .product_assembly_template import ProductAssemblyTemplate  # <-- СТРОКА 1: ИМПОРТ

# Экспортируем все модели единым фронтом для SQLAlchemy и Alembic
__all__ = [
    "Base",
    "Brand",
    "Category",
    "Product",
    "Supplier",
    "ProductUnit",
    "LogisticsStatus",
    "PhysicalStatus",
    "Customer",
    "CashDay",
    "CashEvent",
    "CashEventType",
    "CashEventItem",
    "PendingSale",
    "ProductAssemblyTemplate"  # <-- СТРОКА 2: ЭКСПОРТ В СПИСОК __all__
]
