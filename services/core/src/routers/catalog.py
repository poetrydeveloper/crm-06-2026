# services/core/src/routers/catalog.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, JSON, String, and_
from typing import List
from src.database import get_db
from src.models import Product, Brand, Category, ProductUnit, PhysicalStatus
from src.schemas.catalog import ProductCreate, ProductResponse, BrandCreate, CategoryCreate

router = APIRouter(prefix="/catalog", tags=["Каталог и Умный Поиск"])

def transform_to_snake_case(text: str) -> str:
    """Трансформирует строку: нижний регистр, убирает лишние пробелы, заменяет пробелы на '_'"""
    if not text:
        return ""
    return "_".join(text.lower().strip().split())

# ==========================================
# 🛑 ЧАСТЬ 1: УПРАВЛЕНИЕ БРЕНДАМИ (История 1)
# ==========================================

@router.post("/brands", status_code=status.HTTP_201_CREATED)
async def create_brand(payload: BrandCreate, db: AsyncSession = Depends(get_db)):
    transformed_name = transform_to_snake_case(payload.name)
    existing = await db.execute(select(Brand).where(Brand.name == transformed_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Бренд с таким именем уже существует")
    
    new_brand = Brand(name=transformed_name, description=payload.description)
    db.add(new_brand)
    await db.commit()  # ЖЕСТКАЯ ФИКСАЦИЯ ДЛЯ СГЕНЕРИРОВАНИЯ ID В ПОСТГРЕСЕ
    await db.commit() # Сохраняем "в камне"
    return {"status": "success", "brand_id": new_brand.id, "name": transformed_name}

@router.put("/brands/{brand_id}")
async def update_brand(brand_id: int, payload: BrandCreate, db: AsyncSession = Depends(get_db)):
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")
    
    brand.name = transform_to_snake_case(payload.name)
    brand.description = payload.description
    await db.commit()
    return {"status": "success", "message": "Бренд успешно обновлен"}

@router.delete("/brands/{brand_id}")
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

# ==========================================
# 🛑 ЧАСТЬ 2: УПРАВЛЕНИЕ КАТЕГОРИЯМИ (История 2)
# ==========================================

@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    transformed_name = transform_to_snake_case(payload.name)
    
    # Сбрасываем кэш сессии, чтобы база данных увидела только что созданные записи из параллельных шагов
    await db.commit()
    
    existing = await db.execute(select(Category).where(Category.name == transformed_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Категория с таким названием уже существует")

    if payload.parent_id:
        parent = await db.get(Category, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Родительская категория не найдена")
            
    new_category = Category(name=transformed_name, parent_id=payload.parent_id)
    db.add(new_category)
    await db.commit()  # Генерируем category_id
    await db.commit() # Принудительно пушим в Postgres, блокируя дубликаты для следующих запросов
    return {"status": "success", "category_id": new_category.id, "name": transformed_name}

@router.put("/categories/{category_id}")
async def update_category(category_id: int, payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    category.name = transform_to_snake_case(payload.name)
    if payload.parent_id:
        category.parent_id = payload.parent_id
    await db.commit()
    return {"status": "success", "message": "Категория успешно обновлена"}

@router.delete("/categories/{category_id}")
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

# ==========================================
# 🛑 ЧАСТЬ 3: УПРАВЛЕНИЕ ТОВАРАМИ И АНОМАЛИИ (История 3)
# ==========================================

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    # Принудительно обновляем состояние сессии перед проверками связей
    await db.commit()
    
    category = await db.get(Category, payload.category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Категория с ID {payload.category_id} не найдена")
        
    brand = await db.get(Brand, payload.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Бренд с ID {payload.brand_id} не найден")

    existing = await db.execute(select(Product).where(Product.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Товар с таким артикулом уже зарегистрирован")

    clean_name = payload.name.lower().replace(",", " ").replace(".", " ").replace("-", " ")
    tags = [word for word in clean_name.split() if len(word) > 1]
    tags.append(payload.code.lower())
    tags.append(brand.name)

    new_product = Product(
        category_id=payload.category_id,
        brand_id=payload.brand_id,
        code=payload.code,
        name=transform_to_snake_case(payload.name),
        description=payload.description,
        recommended_retail_price=payload.recommended_retail_price,
        images=payload.images,
        search_tags=tags,
        search_aliases=[a.lower().strip() for a in payload.search_aliases]
    )
    db.add(new_product)
    await db.commit()
    await db.commit()
    return {"status": "success", "product_id": new_product.id, "generated_tags": tags}

@router.put("/products/{product_id}")
async def update_product(product_id: int, payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    linked_units = await db.execute(select(ProductUnit).where(ProductUnit.product_id == product_id).limit(1))
    if linked_units.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Нельзя редактировать товар с созданными единицами на складе")
        
    product.category_id = payload.category_id
    product.brand_id = payload.brand_id
    product.code = payload.code
    product.name = transform_to_snake_case(payload.name)
    product.description = payload.description
    product.recommended_retail_price = payload.recommended_retail_price
    product.images = payload.images
    await db.commit()
    return {"status": "success", "message": "Карточка товара успешно изменена"}

@router.delete("/products/{product_id}")
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

@router.get("/products/anomalies")
async def get_product_anomalies(db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.category_id == 1)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return {
        "has_anomalies": len(products) > 0,
        "count": len(products),
        "products": [{"id": p.id, "code": p.code, "name": p.name} for p in products]
    }

@router.get("/search")
async def smart_search(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    clean_query = q.lower().strip()
    if not clean_query:
        return []
        
    search_words = clean_query.split()
    
    # Ищем карточки товаров по совпадению слов в имени или коде
    word_filters = []
    for word in search_words:
        word_filters.append(
            or_(
                Product.name.ilike(f"%{word}%"),
                Product.code.ilike(f"%{word}%")
            )
        )
        
    products_stmt = select(Product).where(and_(*word_filters)).limit(15)
    products_res = await db.execute(products_stmt)
    products = products_res.scalars().all()
    
    if not products:
        return []
        
    products_list = []
    for prod in products:
        # Считаем живые остатки на полке склада
        qty_stmt = select(func.count(ProductUnit.id)).where(
            ProductUnit.product_id == prod.id,
            ProductUnit.physical_status == PhysicalStatus.IN_STORE,
            ProductUnit.is_reserved == False
        )
        qty_res = await db.execute(qty_stmt)
        qty = qty_res.scalar_one_or_none() or 0
        
        # БЕЗОПАСНЫЙ ПАРСИНГ ТЕГОВ И АЛИАСОВ ДЛЯ ЗАЩИТЫ ОТ ОШИБКИ 500
        tags = prod.search_tags
        if isinstance(tags, str):
            try: tags = ast.literal_eval(tags)
            except: tags = [tags]
            
        aliases = prod.search_aliases
        if isinstance(aliases, str):
            try: aliases = ast.literal_eval(aliases)
            except: aliases = [aliases]
            
        products_list.append({
            "id": prod.id,
            "code": prod.code,
            "name": prod.name,
            "recommended_retail_price": float(prod.recommended_retail_price) if prod.recommended_retail_price else 0.0,
            "search_tags": tags if isinstance(tags, list) else [],
            "search_aliases": aliases if isinstance(aliases, list) else [],
            "images": prod.images if isinstance(prod.images, list) else [],
            "available_qty": int(qty)
        })
        
    return products_list
    
@router.get("/brands", response_model=List[dict])
async def get_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brand))
    return [{"id": b.id, "name": b.name, "description": b.description} for b in result.scalars().all()]

@router.get("/categories", response_model=List[dict])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in result.scalars().all()]

@router.get("/debug-db-raw-product")
async def debug_db_raw_product(db: AsyncSession = Depends(get_db)):
    """Временный отладочный эндпоинт для выгрузки сырых тегов из Postgres"""
    result = await db.execute(select(Product).limit(1))
    prod = result.scalar_one_or_none()
    if not prod:
        return {"error": "Товары в базе отсутствуют"}
    return {
        "id": prod.id,
        "name": prod.name,
        "code": prod.code,
        "search_tags_raw_type": str(type(prod.search_tags)),
        "search_tags_value": prod.search_tags,
        "search_aliases_value": prod.search_aliases
    }