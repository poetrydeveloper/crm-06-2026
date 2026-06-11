# services/core/src/models/product_assembly_template.py
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class ProductAssemblyTemplate(Base):
    """Таблица жестких шаблонов разукомплектации наборов на сателлиты (SQLAlchemy 2.0)"""
    __tablename__ = "product_assembly_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    child_product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
