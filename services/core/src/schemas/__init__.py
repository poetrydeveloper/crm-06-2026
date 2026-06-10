# services/core/src/schemas/__init__.py
from .catalog import ProductCreate, ProductResponse, BrandCreate, CategoryCreate
from .warehouse import CreateSupplierOrder, SupplierOrderResponse, OrderResponseItem
from .cash import CashDayOpen, CashSaleCreate

# Экспортируем схемы единым пакетом
__all__ = [
    "ProductCreate",
    "ProductResponse",
    "BrandCreate",
    "CategoryCreate",
    "CreateSupplierOrder",
    "SupplierOrderResponse",
    "OrderResponseItem",
    "CashDayOpen",
    "CashSaleCreate"
]
