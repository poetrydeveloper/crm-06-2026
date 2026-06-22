# services/core/src/routers/warehouse.py
from fastapi import APIRouter
from src.routers.warehouse_nodes import orders, pre_orders, operations, rules, units, assembly_templates, warehouse_orders

router = APIRouter(prefix="/warehouse")

router.include_router(orders.router)
router.include_router(pre_orders.router)
router.include_router(operations.router)
router.include_router(rules.router)
router.include_router(units.router)
router.include_router(assembly_templates.router)
router.include_router(warehouse_orders.router)