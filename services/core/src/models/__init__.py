# services/core/src/models/__init__.py

# 1. Импортируем базовый декларативный класс
from .base import Base

# 2. Импортируем все модели каталога и справочников (Центр)
from .brand import Brand
from .category import Category
from .product import Product
from .supplier import Supplier

# 3. Импортируем модели складского учета и поштучных единиц
from .product_unit import ProductUnit, LogisticsStatus, PhysicalStatus

# 4. Импортируем финансовые и кассовые модели (Периферия)
from .customer import Customer
from .cash_day import CashDay
from .cash_event import CashEvent, CashEventType
from .cash_event_item import CashEventItem
from .pending_sale import PendingSale, PendingStatus

# 5. Экспортируем всё наружу для Alembic и ядра системы
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
    "PendingStatus",
]
