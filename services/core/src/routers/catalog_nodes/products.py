# services/core/src/routers/catalog_nodes/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.models import Product, Brand, Category, ProductUnit, PhysicalStatus
from src.schemas.catalog import ProductCreate

router = APIRouter(prefix="/products", tags=["Каталог: Товары"])

def transform_to_snake_case(text: str) -> str:
    if not text:
        return ""
    return "_".join(text.lower().strip().split())

@router.get("/all", status_code=200)
async def get_all_products(db: AsyncSession = Depends(get_db)):
    """Возвращает все товары с category_id и доступным количеством на складе"""
    result = await db.execute(select(Product).order_by(Product.id))
    products = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "recommended_retail_price": float(p.recommended_retail_price) if p.recommended_retail_price else 0.0,
            "category_id": p.category_id,
            "search_tags": p.search_tags if isinstance(p.search_tags, list) else [],
            "search_aliases": p.search_aliases if isinstance(p.search_aliases, list) else [],
            "images": p.images if isinstance(p.images, list) else [],
        }
        for p in products
    ]

@router.get("/anomalies")
async def get_product_anomalies(db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.category_id == 1)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return {
        "has_anomalies": len(products) > 0,
        "count": len(products),
        "products": [{"id": p.id, "code": p.code, "name": p.name} for p in products]
    }

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    target_code = payload.code.lower().strip()
    
    existing = await db.execute(select(Product).where(Product.code == target_code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Товар с таким артикулом уже зарегистрирован")

    category = await db.get(Category, payload.category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Категория с ID {payload.category_id} не найдена")
        
    brand = await db.get(Brand, payload.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Бренд с ID {payload.brand_id} не найден")

    clean_name = payload.name.lower().replace(",", " ").replace(".", " ").replace("-", " ")
    stop_words = {"и", "в", "на", "под", "с", "по"}
    tags = [word for word in clean_name.split() if len(word) > 1 and word not in stop_words]
    tags.append(target_code)
    tags.append(brand.name)

    final_images = payload.images if (payload.images and len(payload.images) > 0) else ["/assets/hero.png"]

    raw_aliases = payload.search_aliases if payload.search_aliases is not None else []
    final_aliases = [a.lower().strip() for a in raw_aliases if a]

    new_product = Product(
        category_id=payload.category_id,
        brand_id=payload.brand_id,
        code=target_code,
        name=transform_to_snake_case(payload.name),
        description=payload.description,
        recommended_retail_price=payload.recommended_retail_price,
        images=final_images,
        search_tags=tags,
        search_aliases=final_aliases
    )
    db.add(new_product)
    await db.commit()
    return {"status": "success", "product_id": new_product.id, "generated_tags": tags, "images": final_images}

@router.get("/{product_id}", status_code=200)
async def get_product_by_id_api(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return {
        "product_id": product.id,
        "name": product.name,
        "code": product.code,
        "search_tags": product.search_tags or []
    }

@router.put("/{product_id}")
async def update_product(product_id: int, payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    linked_units = await db.execute(select(ProductUnit).where(ProductUnit.product_id == product_id).limit(1))
    if linked_units.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Нельзя редактировать товар с созданными единицами")
        
    product.category_id = payload.category_id
    product.brand_id = payload.brand_id
    product.code = payload.code.lower().strip()
    product.name = transform_to_snake_case(payload.name)
    product.description = payload.description
    product.recommended_retail_price = payload.recommended_retail_price
    product.images = payload.images if (payload.images and len(payload.images) > 0) else ["/assets/hero.png"]
    await db.commit()
    return {"status": "success", "message": "Карточка товара успешно изменена"}

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
        
    linked_units = await db.execute(select(ProductUnit).where(ProductUnit.product_id == product_id).limit(1))
    if linked_units.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Нельзя удалить товар с созданными единицами на складе")
        
    await db.delete(product)
    await db.commit()
    return {"status": "success", "message": "Товар успешно удален"}