# services/core/src/schemas/catalog.py
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название бренда")
    description: Optional[str] = Field(None, max_length=500)

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    parent_id: Optional[int] = Field(None, description="ID родительской категории, если есть")

class ProductCreate(BaseModel):
    category_id: int
    brand_id: Optional[int] = None
    code: str = Field(..., min_length=1, max_length=100, description="Артикул товара")
    name: str = Field(..., min_length=2, max_length=255, description="Официальное наименование")
    description: Optional[str] = Field(None, max_length=1000)
    recommended_retail_price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    # Сюда можно сразу передать стартовые синонимы, если они есть (например: ["ск"])
    search_aliases: Optional[List[str]] = Field(default_factory=list)

class ProductResponse(BaseModel):
    id: int
    code: str
    name: str
    recommended_retail_price: Optional[Decimal]
    search_tags: Optional[List[str]]
    search_aliases: Optional[List[str]]
    available_qty: int = 0  # Сюда аналитика подставит количество IN_STORE

    class Config:
        from_attributes = True
