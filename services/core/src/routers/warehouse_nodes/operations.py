# services/core/src/routers/warehouse_nodes/operations.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

# 🔥 ИСПРАВЛЕНО: Импортируем менеджеры из их собственных атомарных файлов-компонентов
from src.components.receipt_manager import ReceiptManager
from src.components.disassembly_manager import DisassemblyManager
from src.components.absorption_manager import AbsorptionManager
from src.schemas.warehouse import SupplierInvoiceReceipt, DisassemblyTemplatedPayload, DisassemblyPartialPayload, SetAbsorptionPayload

router = APIRouter(tags=["Склад: Операции и Живые Наборы"])

@router.post("/receipts", status_code=200)
async def process_supplier_invoice_receipt(payload: SupplierInvoiceReceipt, db: AsyncSession = Depends(get_db)):
    """📥 Реализация Команды 0101: Фактическая приемка накладных на полку магазина"""
    return await ReceiptManager.process_receipt(payload.supplier_id, payload.items, db)

@router.post("/disassembly/templated", status_code=200)
async def process_templated_disassembly(payload: DisassemblyTemplatedPayload, db: AsyncSession = Depends(get_db)):
    """🪛 Шаблонная разукомплектация набора по серийному номеру"""
    return await DisassemblyManager.execute_templated_disassembly(payload.unique_serial_number, db)

@router.post("/disassembly/partial", status_code=200)
async def process_partial_disassembly(payload: DisassemblyPartialPayload, db: AsyncSession = Depends(get_db)):
    """🪛 Частичное вытаскивание сателлита (головки) из набора инструментов"""
    return await DisassemblyManager.execute_partial_disassembly(payload.unique_serial_number, payload.child_product_id, db)

@router.post("/sets/absorb", status_code=200)
async def process_set_absorption(payload: SetAbsorptionPayload, db: AsyncSession = Depends(get_db)):
    """🧲 Обратное поглощение: физическая сборка штучной головки внутрь целого набора"""
    return await AbsorptionManager.execute_set_absorption(payload.parent_product_id, payload.satellite_unit_ids, db)
