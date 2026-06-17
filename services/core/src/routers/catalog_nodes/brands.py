# services/core/src/routers/catalog/brands.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import Brand, Product
from src.schemas.catalog import BrandCreate

router = APIRouter(prefix="/brands", tags=["Каталог: Бренды"])

def transform_to_snake_case(text: str) -> str:
    if not text:
        return ""
    return "_".join(text.lower().strip().split())

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_brand(payload: BrandCreate, db: AsyncSession = Depends(get_db)):
    transformed_name = transform_to_snake_case(payload.name)
    existing = await db.execute(select(Brand).where(Brand.name == transformed_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Бренд с таким именем уже существует")
    
    new_brand = Brand(name=transformed_name, description=payload.description)
    db.add(new_brand)
    await db.commit()
    return {"status": "success", "brand_id": new_brand.id, "name": transformed_name}

@router.get("", response_model=list[dict])
async def get_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brand))
    return [{"id": b.id, "name": b.name, "description": b.description} for b in result.scalars().all()]

@router.put("/{brand_id}")
async def update_brand(brand_id: int, payload: BrandCreate, db: AsyncSession = Depends(get_db)):
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")
    
    brand.name = transform_to_snake_case(payload.name)
    brand.description = payload.description
    await db.commit()
    return {"status": "success", "message": "Бренд успешно обновлен"}

@router.delete("/{brand_id}")
async def delete_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")
    
    linked_products = await db.execute(select(Product).where(Product.brand_id == brand_id).limit(1))
    if linked_products.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Нельзя удалить бренд, к которому привязаны товары")
    
    await db.delete(brand)
    await db.commit()
    return {"status": "success", "message": "Бренд успешно удален"}
