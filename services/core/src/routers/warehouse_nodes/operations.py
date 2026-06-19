# services/core/src/routers/warehouse_nodes/operations.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.components.receipt_manager import ReceiptManager
from src.components.disassembly_manager import DisassemblyManager
from src.components.absorption_manager import AbsorptionManager
from src.schemas.warehouse import (
    SupplierInvoiceReceipt,
    DisassemblyTemplatedPayload,
    DisassemblyPartialPayload,
    SetAbsorptionPayload,
)
from pydantic import BaseModel
from typing import List

router = APIRouter(tags=["Склад: Операции и Живые Наборы"])


class ReceiptByUnitsPayload(BaseModel):
    supplier_id: int
    unit_ids: List[int]


@router.post("/receipts", status_code=200)
async def process_supplier_invoice_receipt(payload: ReceiptByUnitsPayload, db: AsyncSession = Depends(get_db)):
    """📥 Приёмка товара по конкретным unit_id (серийным номерам)"""
    return await ReceiptManager.process_receipt_by_units(payload.supplier_id, payload.unit_ids, db)


@router.post("/disassembly/templated", status_code=200)
async def process_templated_disassembly(payload: DisassemblyTemplatedPayload, db: AsyncSession = Depends(get_db)):
    """🪛 Шаблонная разукомплектация набора по серийному номеру"""
    return await DisassemblyManager.execute_templated_disassembly(payload.unique_serial_number, db)


@router.post("/disassembly/partial", status_code=200)
async def process_partial_disassembly(payload: DisassemblyPartialPayload, db: AsyncSession = Depends(get_db)):
    """🪛 Частичное вытаскивание сателлита из набора"""
    return await DisassemblyManager.execute_partial_disassembly(payload.unique_serial_number, payload.child_product_id, db)


@router.post("/sets/absorb", status_code=200)
async def process_set_absorption(payload: SetAbsorptionPayload, db: AsyncSession = Depends(get_db)):
    """🧲 Обратное поглощение: сборка головки внутрь набора"""
    return await AbsorptionManager.execute_set_absorption(payload.parent_product_id, payload.satellite_unit_ids, db)