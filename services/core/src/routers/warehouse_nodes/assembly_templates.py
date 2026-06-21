# services/core/src/routers/warehouse_nodes/assembly_templates.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import ProductAssemblyTemplate

router = APIRouter(tags=["Склад: Шаблоны разукомплектации"])


@router.get("/disassembly/check-template", status_code=200)
async def check_template(product_id: int, db: AsyncSession = Depends(get_db)):
    """Проверить, есть ли шаблон разбора для товара"""
    result = (await db.execute(
        select(ProductAssemblyTemplate).where(
            ProductAssemblyTemplate.parent_product_id == product_id
        )
    )).scalars().all()
    return {
        "has_template": len(result) > 0,
        "template_count": len(result),
    }


@router.post("/disassembly/template-items", status_code=status.HTTP_201_CREATED)
async def add_template_item(payload: dict, db: AsyncSession = Depends(get_db)):
    """Добавить позицию в шаблон разбора"""
    parent_id = payload.get("parent_product_id")
    child_id = payload.get("child_product_id")
    qty = payload.get("quantity", 1)

    if not parent_id or not child_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="parent_product_id и child_product_id обязательны")

    existing = (await db.execute(
        select(ProductAssemblyTemplate).where(
            ProductAssemblyTemplate.parent_product_id == parent_id,
            ProductAssemblyTemplate.child_product_id == child_id,
        )
    )).scalar_one_or_none()

    if existing:
        existing.quantity += qty
    else:
        db.add(ProductAssemblyTemplate(
            parent_product_id=parent_id,
            child_product_id=child_id,
            quantity=qty,
        ))

    await db.commit()
    return {"status": "success", "message": "Позиция добавлена в шаблон"}


@router.get("/disassembly/template-items/{product_id}", status_code=200)
async def get_template_items(product_id: int, db: AsyncSession = Depends(get_db)):
    """Получить все позиции шаблона разбора для товара"""
    result = (await db.execute(
        select(ProductAssemblyTemplate).where(
            ProductAssemblyTemplate.parent_product_id == product_id
        )
    )).scalars().all()

    return [
        {
            "id": t.id,
            "parent_product_id": t.parent_product_id,
            "child_product_id": t.child_product_id,
            "quantity": t.quantity,
        }
        for t in result
    ]