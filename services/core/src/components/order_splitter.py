# services/core/src/components/order_splitter.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Product, Supplier, ProductUnit

class OrderSplitter:
    @staticmethod
    async def get_orders_split(db: AsyncSession) -> dict:
        """
        Атомарная функция: агрегирует поштучные записи product_units 
        в полноценные заказы поставщикам с разделением на Активные и Архивные.
        """
        # Выбираем все поштучные юниты, у которых зафиксирован поставщик, сортируем от свежих к старым
        stmt = select(ProductUnit).where(ProductUnit.supplier_id.is_not(None)).order_by(ProductUnit.id.desc())
        result = await db.execute(stmt)
        units = result.scalars().all()

        orders_map = {}
        for unit in units:
            order_id = unit.supplier_id
            current_status = unit.physical_status.value if hasattr(unit.physical_status, "value") else str(unit.physical_status)

            if order_id not in orders_map:
                supplier_name = f"Поставщик #{order_id}"
                supplier_obj = await db.get(Supplier, order_id)
                if supplier_obj:
                    supplier_name = supplier_obj.name

                orders_map[order_id] = {
                    "supplier_order_id": order_id,
                    "supplier_name": supplier_name,
                    "total_financial_load": 0.0,
                    # По умолчанию считаем закрытым, пока не найдем единицы в пути
                    "status": "Выставлено на полку", 
                    "items": []
                }

            # Бизнес-правило: если хоть одна деталь едет, весь заказ горит в активном статусе
            if current_status in ("EXPECTED", "IN_DELIVERY"):
                orders_map[order_id]["status"] = "В ПУТИ"

            orders_map[order_id]["total_financial_load"] += float(unit.purchase_price or 0)
            
            product_name = f"Товар ID {unit.product_id}"
            product_obj = await db.get(Product, unit.product_id)
            if product_obj:
                product_name = product_obj.name

            # Считаем количество одинаковых номенклатурных позиций внутри поставки
            existing_item = next((i for i in orders_map[order_id]["items"] if i["product_name"] == product_name), None)
            if existing_item:
                existing_item["quantity"] += 1
            else:
                orders_map[order_id]["items"].append({"product_name": product_name, "quantity": 1})

        # Сортируем и раскладываем по двум корзинам
        active_orders = [o for o in orders_map.values() if o["status"] == "В ПУТИ"]
        archived_orders = [o for o in orders_map.values() if o["status"] != "В ПУТИ"]

        return {
            "active": active_orders,
            "archived": archived_orders
        }
