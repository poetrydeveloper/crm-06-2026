# services/qa_orchestrator/utils/db_finders.py
import httpx

async def find_live_brand_id(client: httpx.AsyncClient, brand_name: str, fallback_id: int = 1) -> int:
    """Ищет существующий бренд в СУБД по имени и возвращает его ID"""
    try:
        b_list = await client.get("/api/v1/catalog/brands")
        if b_list.status_code == 200:
            return next((b["id"] for b in b_list.json() if b["name"] == brand_name.lower().strip()), fallback_id)
    except:
        pass
    return fallback_id

async def find_live_category_id(client: httpx.AsyncClient, keyword: str, fallback_id: int = 2) -> int:
    """Ищет существующую категорию по ключевому слову и возвращает её ID"""
    try:
        c_list = await client.get("/api/v1/catalog/categories")
        if c_list.status_code == 200:
            return next((c["id"] for c in c_list.json() if keyword.lower().strip() in c["name"]), fallback_id)
    except:
        pass
    return fallback_id

async def find_live_product_id(client: httpx.AsyncClient, product_code: str, fallback_id: int = 1) -> int:
    """Ищет существующий товар по артикулу (code) и возвращает его ID"""
    try:
        p_list = await client.get("/api/v1/catalog/products")
        if p_list.status_code == 200:
            return next((p["id"] for p in p_list.json() if p["code"] == product_code.upper().strip()), fallback_id)
    except:
        pass
    return fallback_id

async def find_live_supplier_id(client: httpx.AsyncClient, keyword: str, fallback_id: int = 1) -> int:
    """Ищет существующего поставщика по ключевому слову и возвращает его ID"""
    try:
        sup_list = await client.get("/api/v1/warehouse/suppliers")
        if sup_list.status_code == 200:
            return next((s["id"] for s in sup_list.json() if keyword.lower().strip() in s["name"].lower()), fallback_id)
    except:
        pass
    return fallback_id
