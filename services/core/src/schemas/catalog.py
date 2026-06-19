# services/core/src/schemas/catalog.py
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название бренда")
    description: Optional[str] = Field(None, max_length=500, description="Описание бренда")

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    parent_id: Optional[int] = Field(None, description="ID родительской категории, если есть")

class ProductCreate(BaseModel):
    category_id: int
    brand_id: int = Field(..., description="ID бренда")
    code: str = Field(..., min_length=1, max_length=100, description="Артикул товара")
    name: str = Field(..., min_length=2, max_length=255, description="Официальное наименование")
    description: Optional[str] = Field(None, max_length=1000, description="Описание товара")
    recommended_retail_price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2, description="Рекомендуемая розница")
    # 🔥 ИСПРАВЛЕНО: Поля объявлены как необязательные со значением по умолчанию None
    search_aliases: Optional[List[str]] = Field(None, description="Стартовые сленговые синонимы")
    images: Optional[List[str]] = Field(None, description="Массив ссылок на изображения")

class ProductResponse(BaseModel):
    id: int
    code: str
    name: str
    recommended_retail_price: Optional[Decimal]
    search_tags: Optional[List[str]]
    search_aliases: Optional[List[str]]
    images: List[str] = Field(default_factory=list, description="Ссылки на изображения товара")
    available_qty: int = 0  # Количество доступных единиц IN_STORE на складе

    class Config:
        from_attributes = True
