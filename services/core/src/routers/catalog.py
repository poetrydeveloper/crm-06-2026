# services/core/src/routers/catalog.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List
from src.database import get_db
from src.models import Product, Brand, Category, ProductUnit, PhysicalStatus
from src.schemas.catalog import ProductCreate, ProductResponse, BrandCreate, CategoryCreate

router = APIRouter(prefix="/catalog", tags=["Каталог и Умный Поиск"])

# --- 1. ДОБАВЛЕНИЕ БРЕНДА ---
@router.post("/brands", status_code=status.HTTP_201_CREATED)
async def create_brand(payload: BrandCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем уникальность имени
    existing = await db.execute(select(Brand).where(Brand.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Бренд с таким именем уже существует")
    
    new_brand = Brand(name=payload.name, description=payload.description)
    db.add(new_brand)
    return {"status": "success", "brand_id": new_brand.id}

# --- 2. ДОБАВЛЕНИЕ КАТЕГОРИИ ---
@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    if payload.parent_id:
        parent = await db.get(Category, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Родительская категория не найдена")
            
    new_category = Category(name=payload.name, parent_id=payload.parent_id)
    db.add(new_category)
    return {"status": "success", "category_id": new_category.id}

# --- 3. СОЗДАНИЕ ТОВАРА С АВТО-ТЕГАМИ ---
@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем артикул на уникальность
    existing = await db.execute(select(Product).where(Product.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Товар с таким артикулом уже зарегистрирован")

    # 2. АВТОМАТИЧЕСКАЯ ГЕНЕРАЦИЯ ТЕГОВ (Алгоритм из ТЗ)
    # Очищаем имя, переводим в нижний регистр и бьем на слова
    clean_name = payload.name.lower().replace(",", " ").replace(".", " ").replace("-", " ")
    tags = [word for word in clean_name.split() if len(word) > 1] # Игнорируем предлоги из 1 буквы
    
    # Добавляем артикул в теги для надежности
    tags.append(payload.code.lower())

    # Подтягиваем текстовое имя бренда, если он указан, для добавления в теги
    if payload.brand_id:
        brand_obj = await db.get(Brand, payload.brand_id)
        if brand_obj:
            tags.append(brand_obj.name.lower())

    # 3. Сохраняем карточку в базу
    new_product = Product(
        category_id=payload.category_id,
        brand_id=payload.brand_id,
        code=payload.code,
        name=payload.name,
        description=payload.description,
        recommended_retail_price=payload.recommended_retail_price,
        search_tags=tags,                                   # Записываем авто-теги
        search_aliases=[a.lower() for a in payload.search_aliases]  # Записываем синонимы
    )
    db.add(new_product)
    await db.flush() # Получаем id новой карточки до коммита
    return {"status": "success", "product_id": new_product.id, "generated_tags": tags}

# --- 4. УМНЫЙ ПОИСК ДЛЯ КАССЫ С ПОДСЧЕТОМ ОСТАТКОВ (JOIN + COUNT) ---
@router.get("/search", response_model=List[ProductResponse])
async def smart_search(
    q: str = Query(..., min_length=2, description="Поисковый запрос кассира"),
    db: AsyncSession = Depends(get_db)
):
    query_word = q.lower().strip()
    
    # Подготавливаем JSON-запрос для поиска внутри массивов PostgreSQL JSONB
    # В Postgres конструкция search_tags @> '"слово"' проверяет наличие элемента в массиве
    json_search_pattern = f'"{query_word}"'

    # Строим сложный асинхронный SQL-запрос с подсчетом доступных остатков FIFO
    stmt = (
        select(
            Product,
            func.count(ProductUnit.id).filter(
                ProductUnit.physical_status == PhysicalStatus.IN_STORE,
                ProductUnit.is_reserved == False
            ).label("available_qty")
        )
        .outerjoin(ProductUnit, Product.id == ProductUnit.product_id)
        # Умная фильтрация: по началу имени, по артикулу, внутри авто-тегов или синонимов
        .where(
            or_(
                Product.name.ilike(f"%{query_word}%"),
                Product.code.ilike(f"{query_word}%"),
                func.jsonb_contains(Product.search_tags, func.cast(json_search_pattern, func.JSON)),
                func.jsonb_contains(Product.search_aliases, func.cast(json_search_pattern, func.JSON))
            )
        )
        .group_by(Product.id)
        .limit(15) # Ограничиваем выдачу, чтобы касса "летала"
    )

    result = await db.execute(stmt)
    
    products_list = []
    for row in result.all():
        product_obj = row[0]
        qty = row[1]
        
        # Маппим данные в нашу красивую Pydantic-схему для фронтенда
        products_list.append(
            ProductResponse(
                id=product_obj.id,
                code=product_obj.code,
                name=product_obj.name,
                recommended_retail_price=product_obj.recommended_retail_price,
                search_tags=product_obj.search_tags,
                search_aliases=product_obj.search_aliases,
                available_qty=qty
            )
        )
        
    return products_list

# --- 5. САМООБУЧЕНИЕ КАССЫ (ПРИВЯЗКА СЛЕНГОВОГО СИНОНИМА РУКАМИ) ---
@router.patch("/products/{product_id}/learn")
async def teach_search_alias(product_id: int, alias: str = Query(...), db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
        
    clean_alias = alias.lower().strip()
    
    # Инициализируем список синонимов, если он пуст, и добавляем новое слово (например: "ск")
    current_aliases = list(product.search_aliases) if product.search_aliases else []
    if clean_alias not in current_aliases:
        current_aliases.append(clean_alias)
        product.search_aliases = current_aliases # Перезаписываем JSON-поле в Postgres
        
    return {"status": "success", "message": f"Товар обучен слову '{clean_alias}'"}

@router.get("/brands", response_model=List[dict])
async def get_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brand))
    return [{"id": b.id, "name": b.name, "description": b.description} for b in result.scalars().all()]

@router.get("/categories", response_model=List[dict])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in result.scalars().all()]

@router.get("/products/all", response_model=List[dict])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    stmt = select(Product, Brand.name.label("brand_name"), Category.name.label("category_name")).\
        outerjoin(Brand, Product.brand_id == Brand.id).\
        join(Category, Product.category_id == Category.id)
    result = await db.execute(stmt)
    
    products = []
    for row in result.all():
        prod = row[0]
        products.append({
            "id": prod.id,
            "code": prod.code,
            "name": prod.name,
            "brand_name": row.brand_name or "Без бренда",
            "category_name": row.category_name,
            "recommended_retail_price": float(prod.recommended_retail_price or 0),
            "search_tags": prod.search_tags
        })
    return products