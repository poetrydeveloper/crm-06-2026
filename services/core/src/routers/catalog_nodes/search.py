# services/core/src/routers/catalog/search.py
import ast
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from src.database import get_db
from src.models import Product, ProductUnit, PhysicalStatus

router = APIRouter(tags=["Каталог: Умный Поиск"])

@router.get("/search")
async def smart_search(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    clean_query = q.lower().strip()
    if not clean_query:
        return []
        
    search_words = clean_query.split()
    word_filters = []
    for word in search_words:
        word_filters.append(or_(Product.name.ilike(f"%{word}%"), Product.code.ilike(f"%{word}%")))
        
    products_stmt = select(Product).where(and_(*word_filters)).limit(15)
    products_res = await db.execute(products_stmt)
    products = products_res.scalars().all()
    
    if not products:
        return []
        
    products_list = []
    for prod in products:
        qty_stmt = select(func.count(ProductUnit.id)).where(
            ProductUnit.product_id == prod.id,
            ProductUnit.physical_status == PhysicalStatus.IN_STORE,
            ProductUnit.is_reserved == False
        )
        qty_res = await db.execute(qty_stmt)
        qty = qty_res.scalar_one_or_none() or 0
        
        tags = prod.search_tags
        if isinstance(tags, str):
            try: tags = ast.literal_eval(tags)
            except: tags = [tags]
           
        aliases = prod.search_aliases
        if isinstance(aliases, str):
            try: aliases = ast.literal_eval(aliases)
            except: aliases = [aliases]
            
        products_list.append({
            "id": prod.id, "code": prod.code, "name": prod.name,
            "recommended_retail_price": float(prod.recommended_retail_price) if prod.recommended_retail_price else 0.0,
            "search_tags": tags if isinstance(tags, list) else [],
            "search_aliases": aliases if isinstance(aliases, list) else [],
            "images": prod.images if isinstance(prod.images, list) else [],
            "available_qty": int(qty)
        })
    return products_list

@router.get("/debug-db-raw-product")
async def debug_db_raw_product(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).limit(1))
    prod = result.scalar_one_or_none()
    if not prod:
        return {"error": "Товары в базе отсутствуют"}
    return {
        "id": prod.id, "name": prod.name, "code": prod.code,
        "search_tags_raw_type": str(type(prod.search_tags)),
        "search_tags_value": prod.search_tags,
        "search_aliases_value": prod.search_aliases
    }
