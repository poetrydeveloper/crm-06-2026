// frontend/src/pages/admin/Catalog.tsx
import React, { useState, useEffect } from 'react';
import { CategoryTree } from '../../components/atomic/CategoryTree';
import { ProductGrid } from '../../components/atomic/ProductGrid';

export const Catalog: React.FC = () => {
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Заглушка симуляции данных (при интеграции заменяется на fetch к /api/v1/)
  useEffect(() => {
    setCategories([
      { id: 1, name: 'Инструменты', parent_id: null },
      { id: 2, name: 'Ключи', parent_id: 1 },
      { id: 3, name: 'Головки', parent_id: 1 }
    ]);
    setProducts([
      { id: 101, name: 'Ключ рожковый 10мм Toptul', code: 'КЛ-10-ТП', recommended_retail_price: 500, category_id: 2 },
      { id: 102, name: 'Головка торцевая 1/2 12мм', code: 'ГЛ-12', recommended_retail_price: 350, category_id: 3 }
    ]);
  }, []);

  // Умная фильтрация: по выбранной категории ИЛИ по тексту глобального поиска
  const filteredProducts = products.filter(prod => {
    const matchesSearch = prod.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          prod.code.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategoryId ? prod.category_id === selectedCategoryId : true;
    
    // Если вбит поиск, ищем по всей базе (игнорируя фильтр категорий по ТЗ)
    return searchQuery ? matchesSearch : matchesCategory;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 60px)' }}>
      {/* Верхний бар Умного поиска */}
      <div style={{ background: '#1a1a1a', padding: '10px 20px', borderBottom: '1px solid #333' }}>
        <input
          type="text"
          placeholder="🔍 Умный поиск товаров по названию или артикулу..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            maxWidth: '500px',
            padding: '8px 12px',
            borderRadius: '4px',
            border: '1px solid #444',
            background: '#2d2d2d',
            color: '#fff',
            outline: 'none'
          }}
        />
      </div>

      {/* Основная рабочая область */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <CategoryTree
          categories={categories}
          selectedCategoryId={selectedCategoryId}
          onSelectCategory={(id) => { setSelectedCategoryId(id); setSearchQuery(''); }}
          onCreateCategory={() => alert('Создание категории')}
          onEditCategory={(id) => alert(`Редактирование категории ${id}`)}
          onDeleteCategory={(id) => alert(`Удаление категории ${id}`)}
        />
        
        <ProductGrid
          products={filteredProducts}
          onCreateProduct={() => alert('Создание товара')}
          onEditProduct={(id) => alert(`Редактирование товара ${id}`)}
          onDeleteProduct={(id) => alert(`Удаление товара ${id}`)}
        />
      </div>
    </div>
  );
};
