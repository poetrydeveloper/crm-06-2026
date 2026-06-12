# services/qa_orchestrator/features/steps/15_warehouse_set_absorption_steps.py
import httpx
import asyncpg
import random

GATEWAY_URL = "http://gateway:80"
DATABASE_URL = "postgresql://crm_admin:crm_secure_password@db:5432/crm_main_database"

# Сессия для точечной зачистки хвостов после теста
test_session = {
    "supplier_id": None,
    "brand_id": None,
    "category_id": None,
    "parent_product_id": None,
    "child_product_id": None,
    "broken_parent_unit_id": None,
    "satellite_unit_ids": [],
    "new_assembled_unit_id": None
}

async def run_15_warehouse_set_absorption_assertions():
    """
    Стадия 15: Комплектация набора из свободных деталей.
    Тест полностью автономен, сам создает некомплект и лечит его.
    """
    results = []
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # 1. Проверяем связь со шлюзом
        async with httpx.AsyncClient(base_url=GATEWAY_URL) as client:
            res = await client.get("/api/v1/healthcheck", timeout=2.0)
            if res.status_code != 200:
                return [f"❌ Бэкенд через шлюз недоступен. Статус: {res.status_code}"]
        results.append("✔ Дано Бэкенд Core доступен по адресу через шлюз Nginx")

        # 2. РАЗВЕДКА И СОЗДАНИЕ СПРАВОЧНИКОВ С ТАЙМСТАМПАМИ NOW()
        await strict_db_scouting(conn)

        # 3. И На складе лежат 2 отдельные детали в статусе "IN_STORE"
        # Эмулируем, что детали были оприходованы ранее и просто лежат на балансе
        u1 = await conn.fetchval("""
            INSERT INTO product_units (product_id, supplier_id, unique_serial_number, purchase_price, logistics_status, physical_status, is_reserved, created_at, updated_at)
            VALUES ($1, $2, $3, 150.00, 'RECEIVED', 'IN_STORE', false, NOW(), NOW()) RETURNING id;
        """, test_session["child_product_id"], test_session["supplier_id"], f"SN-FREE-10A-{random.randint(100,999)}")
        
        u2 = await conn.fetchval("""
            INSERT INTO product_units (product_id, supplier_id, unique_serial_number, purchase_price, logistics_status, physical_status, is_reserved, created_at, updated_at)
            VALUES ($1, $2, $3, 150.00, 'RECEIVED', 'IN_STORE', false, NOW(), NOW()) RETURNING id;
        """, test_session["child_product_id"], test_session["supplier_id"], f"SN-FREE-10B-{random.randint(100,999)}")
        
        test_session["satellite_unit_ids"] = [u1, u2]
        results.append("✔ И На складе лежат 2 отдельные детали в статусе 'IN_STORE'")

        # 4. Моделируем "Вскрытый / Поврежденный" родительский набор (Статус IN_DISASSEMBLED или LOST)
        # Показываем системе, что этот набор когда-то "раздербанили" и из него ушли детали
        broken_parent = await conn.fetchval("""
            INSERT INTO product_units (product_id, supplier_id, unique_serial_number, purchase_price, logistics_status, physical_status, is_reserved, created_at, updated_at)
            VALUES ($1, $2, $3, 1200.00, 'RECEIVED', 'IN_DISASSEMBLED', false, NOW(), NOW()) RETURNING id;
        """, test_session["parent_product_id"], test_session["supplier_id"], f"SN-BROKEN-{random.randint(100,999)}")
        
        test_session["broken_parent_unit_id"] = broken_parent
        results.append("✔ И В системе зарегистрирован шаблон сборки, в который входят данные детали")

        # 5. Когда Кладовщик отправляет запрос на комплектацию целого набора из этих физических юнитов
        async with httpx.AsyncClient(base_url=GATEWAY_URL) as client:
            payload = {
                "parent_product_id": test_session["parent_product_id"],
                "satellite_unit_ids": test_session["satellite_unit_ids"]
            }
            response = await client.post("/api/v1/warehouse/sets/absorb", json=payload, timeout=5.0)
            
            if response.status_code not in (200, 201):
                return results + [f"❌ Сбой комплектации на бэкенде. Статус: {response.status_code}, Ошибка: {response.text}"]
            
            test_session["new_assembled_unit_id"] = response.json().get("parent_unit_id")
        results.append("✔ Когда Кладовщик отправляет запрос на комплектацию целого набора из этих физических юнитов")

        # 6. Тогда Физический статус одиночных сателлитов меняется в СУБД на "ABSORBED"
        for unit_id in test_session["satellite_unit_ids"]:
            row = await conn.fetchrow("SELECT physical_status, is_reserved FROM product_units WHERE id = $1", unit_id)
            if row["physical_status"] != "ABSORBED" or row["is_reserved"] is not True:
                return results + [f"❌ Сбой: Сателлит {unit_id} ушел в статус {row['physical_status']}, reserved={row['is_reserved']}"]
        results.append("✔ Тогда Физический статус одиночных сателлитов меняется в СУБД на 'ABSORBED'")
        results.append("✔ И Они блокируются для независимой розничной продажи на кассе")

        # 7. Проверяем рождение нового полноценного набора готового к продаже
        p_status = await conn.fetchval("SELECT physical_status FROM product_units WHERE id = $1", test_session["new_assembled_unit_id"])
        if p_status != "IN_STORE":
            return results + [f"❌ Сбой: Новый собранный набор имеет статус {p_status} вместо IN_STORE"]
        results.append("✔ И На баланс склада автоматически генерируется 1 новый родительский юнит набора в статусе 'IN_STORE'")

        # 8. Проверяем жесткую рекурсивную связь parent_unit_id у поглощенных детей
        for unit_id in test_session["satellite_unit_ids"]:
            p_id = await conn.fetchval("SELECT parent_unit_id FROM product_units WHERE id = $1", unit_id)
            if p_id != test_session["new_assembled_unit_id"]:
                return results + [f"❌ Сбой: У сателлита {unit_id} поле parent_unit_id ({p_id}) не указывает на новый набор!"]
        results.append("✔ И У поглощенных сателлитов поле parent_unit_id жестко привязывается к ID созданного набора")

    except Exception as e:
        results.append(f"❌ КРИТИЧЕСКАЯ АВАРИЯ ТЕСТА: {str(e)}")
    finally:
        # =========================================================================
        # 🧹 ЧИСТЫЙ ТЕЙРДАУН: Стираем физический мусор, возвращаем БД в исходный вид
        # =========================================================================
        to_delete = []
        if test_session["new_assembled_unit_id"]: to_delete.append(test_session["new_assembled_unit_id"])
        if test_session["broken_parent_unit_id"]: to_delete.append(test_session["broken_parent_unit_id"])
        to_delete.extend(test_session["satellite_unit_ids"])
        
        if to_delete:
            await conn.execute("DELETE FROM product_units WHERE id = ANY($1)", to_delete)
        await conn.close()
        
    return results

async def strict_db_scouting(conn):
    """Автономная разведка номенклатуры с соблюдением NOT NULL ограничений"""
    sup_id = await conn.fetchval("SELECT id FROM suppliers WHERE name = 'Комплектация-Авто' LIMIT 1")
    if not sup_id:
        sup_id = await conn.fetchval("INSERT INTO suppliers (name, created_at, updated_at) VALUES ('Комплектация-Авто', NOW(), NOW()) RETURNING id")
    test_session["supplier_id"] = sup_id

    b_id = await conn.fetchval("SELECT id FROM brands WHERE name = 'Toptul' LIMIT 1")
    if not b_id:
        b_id = await conn.fetchval("INSERT INTO brands (name, created_at, updated_at) VALUES ('Toptul', NOW(), NOW()) RETURNING id")
    test_session["brand_id"] = b_id

    c_id = await conn.fetchval("SELECT id FROM categories WHERE name = 'Инструменты' LIMIT 1")
    if not c_id:
        c_id = await conn.fetchval("INSERT INTO categories (name, created_at, updated_at) VALUES ('Инструменты', NOW(), NOW()) RETURNING id")
    test_session["category_id"] = c_id

    p_child = await conn.fetchval("SELECT id FROM products WHERE code = 'ГЛ-10' LIMIT 1")
    if not p_child:
        p_child = await conn.fetchval("""
            INSERT INTO products (name, code, category_id, brand_id, search_tags, search_aliases, created_at, updated_at) 
            VALUES ('Головка торцевая 10мм', 'ГЛ-10', $1, $2, '[]'::jsonb, '[]'::jsonb, NOW(), NOW()) RETURNING id
        """, c_id, b_id)
    test_session["child_product_id"] = p_child

    p_parent = await conn.fetchval("SELECT id FROM products WHERE code = 'НАБ-02' LIMIT 1")
    if not p_parent:
        p_parent = await conn.fetchval("""
            INSERT INTO products (name, code, category_id, brand_id, search_tags, search_aliases, created_at, updated_at) 
            VALUES ('Набор инструментов Toptul 2 предм', 'НАБ-02', $1, $2, '[]'::jsonb, '[]'::jsonb, NOW(), NOW()) RETURNING id
        """, c_id, b_id)
    test_session["parent_product_id"] = p_parent
