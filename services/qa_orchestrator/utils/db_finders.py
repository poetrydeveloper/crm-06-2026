# services/qa_orchestrator/utils/db_finders.py
import httpx

async def find_live_brand_id(client: httpx.AsyncClient, brand_name: str, fallback_id: int = 1) -> int:
    try:
        b_list = await client.get("/api/v1/catalog/brands")
        if b_list.status_code == 200:
            return next((b["id"] for b in b_list.json() if b["name"] == brand_name.lower().strip()), fallback_id)
    except: pass
    return fallback_id

async def find_live_category_id(client: httpx.AsyncClient, keyword: str, fallback_id: int = 2) -> int:
    try:
        c_list = await client.get("/api/v1/catalog/categories")
        if c_list.status_code == 200:
            return next((c["id"] for c in c_list.json() if keyword.lower().strip() in c["name"].lower()), fallback_id)
    except: pass
    return fallback_id

async def find_live_product_id(client: httpx.AsyncClient, product_code: str, fallback_id: int = 1) -> int:
    try:
        p_list = await client.get("/api/v1/catalog/products")
        if p_list.status_code == 200:
            return next((p["id"] for p in p_list.json() if p["code"] == product_code.lower().strip()), fallback_id)
    except: pass
    return fallback_id

async def find_live_supplier_id(client: httpx.AsyncClient, keyword: str, fallback_id: int = 1) -> int:
    try:
        sup_list = await client.get("/api/v1/warehouse/suppliers")
        if sup_list.status_code == 200:
            return next((s["id"] for s in sup_list.json() if keyword.lower().strip() in s["name"].lower()), fallback_id)
    except: pass
    return fallback_id

async def teardown_live_categories_by_name(client: httpx.AsyncClient, name_snake: str):
    try:
        c_list = await client.get("/api/v1/catalog/categories")
        category_id = next((c["id"] for c in c_list.json() if c["name"] == name_snake.lower().strip()), None)
        if category_id and category_id != 1:
            await client.delete(f"/api/v1/catalog/categories/{category_id}")
    except: pass

async def teardown_live_brand_by_name(client: httpx.AsyncClient, brand_name_snake: str):
    try:
        b_list = await client.get("/api/v1/catalog/brands")
        brand_id = next((b["id"] for b in b_list.json() if b["name"] == brand_name_snake.lower().strip()), None)
        if brand_id:
            await client.delete(f"/api/v1/catalog/brands/{brand_id}")
    except: pass

# 🔥 ИСПРАВЛЕНО: Безопасное удаление товара с приведением к нижнему регистру (Решает сбой Истории 4)
async def teardown_live_product_by_code(client: httpx.AsyncClient, product_code: str):
    try:
        p_list = await client.get("/api/v1/catalog/products")
        product_id = next((p["id"] for p in p_list.json() if p["code"] == product_code.lower().strip()), None)
        if product_id:
            await client.delete(f"/api/v1/catalog/products/{product_id}")
    except: pass

async def teardown_live_product_units_by_product_id(client: httpx.AsyncClient, product_id: int):
    try: await client.delete(f"/api/v1/warehouse/units/debug-clear?product_id={product_id}")
    except: pass

async def teardown_live_supplier_order_by_product(client: httpx.AsyncClient, product_id: int):
    try: await client.delete(f"/api/v1/warehouse/orders/debug-clear?product_id={product_id}")
    except: pass
