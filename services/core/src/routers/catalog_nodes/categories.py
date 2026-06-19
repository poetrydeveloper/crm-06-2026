# services/core/src/routers/catalog/categories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import Category, Product
from src.schemas.catalog import CategoryCreate

router = APIRouter(prefix="/categories", tags=["Каталог: Категории"])

def slugify_name(name: str) -> str:
    """Трансформация: 'Рожковые Ключи' -> 'рожковые_ключи'"""
    return name.strip().lower().replace(" ", "_")

def unslugify_name(slug: str) -> str:
    """🔥 ИСПРАВЛЕНО: Возвращаем все буквы строго в малом регистре ('рожковые ключи')"""
    return slug.replace("_", " ").lower()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    system_name = slugify_name(payload.name)
    
    existing = await db.execute(
        select(Category).where(Category.name == system_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Категория с таким названием уже существует")

    if payload.parent_id:
        parent = await db.get(Category, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Родительская категория не найдена")
    
    new_category = Category(name=system_name, parent_id=payload.parent_id)
    db.add(new_category)
    await db.commit()
    return {"status": "success", "category_id": new_category.id, "name": unslugify_name(new_category.name)}

@router.get("", response_model=list[dict])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    # Для клиента на фронтенде возвращаем все на место (заменяем '_' на пробел) в малом регистре
    return [
        {"id": c.id, "name": unslugify_name(c.name), "parent_id": c.parent_id} 
        for c in result.scalars().all()
    ]

@router.put("/{category_id}")
async def update_category(category_id: int, payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    category.name = slugify_name(payload.name)
    if payload.parent_id:
        category.parent_id = payload.parent_id
    await db.commit()
    return {"status": "success", "message": "Категория успешно обновлена"}

@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    if category_id == 1:
        raise HTTPException(status_code=400, detail="Нельзя удалить системную резервную категорию")

    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    linked_products = await db.execute(select(Product).where(Product.category_id == category_id).limit(1))
    if linked_products.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Нельзя удалить категорию, к которой привязаны товары")
    
    await db.delete(category)
    await db.commit()
    return {"status": "success", "message": "Категория успешно удалена"}
