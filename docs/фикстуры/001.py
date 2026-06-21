import datetime
import json
from sqlalchemy import (
    create_engine, Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# ==========================================
# 📦 ОПРЕДЕЛЕНИЕ МОДЕЛЕЙ (Связи по вашей схеме)
# ==========================================

class Brand(Base):
    __tablename__ = 'brands'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=True)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    recommended_retail_price = Column(Numeric(10, 2), nullable=True)
    search_tags = Column(String, nullable=True)
    search_aliases = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False)
    contact_info = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProductUnit(Base):
    __tablename__ = 'product_units'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    parent_unit_id = Column(Integer, ForeignKey('product_units.id'), nullable=True)
    unique_serial_number = Column(String(100), unique=True, nullable=False)
    purchase_price = Column(Numeric(10, 2), nullable=True)
    logistics_status = Column(String(50), default='RECEIVED')
    physical_status = Column(String(50), default='IN_STORE')
    is_reserved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

# ==========================================
# 🛠️ ГЕНЕРАЦИЯ РАСШИРЕННЫХ ДАННЫХ
# ==========================================

def run_fixtures():
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    print("--- 🚀 Запуск генерации фикстур с новыми брендами ---")

    # 1. Наполнение брендов из вашего списка
    brands_data = [
        Brand(id=1, name="Jonnesway", description="Профессиональный тайваньский ручной инструмент"),
        Brand(id=2, name="Forsage", description="Популярный полупрофессиональный и профессиональный автоинструмент"),
        Brand(id=3, name="RockForce", description="Усиленный инструмент для тяжелых условий СТО"),
        Brand(id=4, name="Force", description="Легендарный тайваньский бренд с высочайшим ресурсом"),
        Brand(id=5, name="Baum", description="Профессиональный слесарный инструмент"),
        Brand(id=6, name="FORCEKRAFT", description="Инновационный инструмент индустриального качества"),
        Brand(id=7, name="TOPTUL", description="Мировой лидер в производстве премиального слесарно-монтажного инструмента"),
        Brand(id=8, name="Startul", description="Доступный инструмент для домашних мастеров и полупрофи")
    ]
    session.add_all(brands_data)
    session.flush()

    # 2. Добавляем Поставщика
    supplier = Supplier(id=1, name="ООО Прайд-Инструмент", contact_info="г. Москва, ул. Промышленная 12")
    session.add(supplier)

    # 3. Дерево категорий (из прошлых шагов)
    cat_root = Category(id=1, name="Ручной инструмент", parent_id=None)
    session.add(cat_root)
    session.flush()

    cat_keys = Category(id=2, name="Ключи", parent_id=cat_root.id)
    session.add(cat_keys)
    session.flush()

    cat_comb = Category(id=3, name="Комбинированные", parent_id=cat_keys.id)
    cat_comb_sets = Category(id=4, name="Комбинированные наборы", parent_id=cat_keys.id)
    cat_ratch_sets = Category(id=5, name="Трещеточные наборы", parent_id=cat_keys.id)
    cat_ratch = Category(id=6, name="Трещеточные", parent_id=cat_keys.id)
    session.add_all([cat_comb, cat_comb_sets, cat_ratch_sets, cat_ratch])
    session.flush()

    # 4. Наполнение номенклатуры (Привязываем новые бренды к вашим товарам для разнообразия)
    p1 = Product(
        id=1, category_id=cat_comb.id, brand_id=1, code="W26110", # Jonnesway
        name="Ключ комбинированный 10мм Jonnesway",
        description="Хромованадиевая сталь, матовое покрытие", recommended_retail_price=450.00,
        search_tags=json.dumps(["ключ", "10мм"]), search_aliases=json.dumps(["w26110"])
    )
    
    p2 = Product(
        id=2, category_id=cat_comb_sets.id, brand_id=4, code="F-5122", # Force
        name="Ключи комбинированные Force, набор 12пр. (6, 8, 10, 12-19, 22мм)",
        description="Классический набор в брезентовом чехле", recommended_retail_price=4800.00,
        search_tags=json.dumps(["набор ключей", "force"]), search_aliases=json.dumps(["5122"])
    )

    p3 = Product(
        id=3, category_id=cat_ratch_sets.id, brand_id=3, code="RF-66110S", # RockForce
        name="Ключи комбинированные трещоточные RockForce (8,10,12-19мм), набор 10пр.",
        description="Усиленный механизм 72 зубца, пластиковый кейс", recommended_retail_price=8200.00,
        search_tags=json.dumps(["трещотка", "набор"]), search_aliases=json.dumps(["66110s"])
    )

    p4 = Product(
        id=4, category_id=cat_ratch.id, brand_id=7, code="GAAA1212", # TOPTUL
        name="Ключ комбинированный трещоточный 10мм TOPTUL",
        description="Премиальное качество, зеркальная полировка", recommended_retail_price=1250.00,
        search_tags=json.dumps(["трещотка", "топтул"]), search_aliases=json.dumps(["gaaa1212"])
    )
    session.add_all([p1, p2, p3, p4])
    session.flush()

    # 5. Складские остатки (Product Units)
    units = [
        ProductUnit(id=1, product_id=p2.id, supplier_id=supplier.id, unique_serial_number="SN-FORCE-12PR", purchase_price=3100.00),
        ProductUnit(id=2, product_id=p1.id, supplier_id=supplier.id, unique_serial_number="SN-JONN-10MM", purchase_price=280.00),
        ProductUnit(id=3, product_id=p3.id, supplier_id=supplier.id, unique_serial_number="SN-ROCK-RATCH", purchase_price=5400.00),
        ProductUnit(id=4, product_id=p4.id, supplier_id=supplier.id, unique_serial_number="SN-TOPT-10MM", purchase_price=780.00)
    ]
    session.add_all(units)
    
    session.commit()
    print("--- ✅ Расширенные фикстуры успешно применены ---")

    # Вывод для демонстрации связей брендов
    print("\nПроверка фильтрации по брендам (для API роутов):")
    for b in session.query(Brand).all():
        products_count = session.query(Product).filter(Product.brand_id == b.id).count()
        print(f"🏷️ Бренд: {b.name.ljust(12)} | Описание: {b.description[:45]}... | Товаров в базе: {products_count}")

if __name__ == "__main__":
    run_fixtures()