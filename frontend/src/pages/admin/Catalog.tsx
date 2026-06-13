// frontend/src/pages/admin/Catalog.tsx
import React, { useState, useEffect } from 'react';
import { CategoryTree } from '../../components/atomic/CategoryTree';
import { ProductGrid } from '../../components/atomic/ProductGrid';

interface Category {
  id: number;
  name: string;
  parent_id: number | null;
}

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
  category_id: number;
}

export const Catalog: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // 📥 1. Загрузка категорий из бэкенда ядра
  const loadCategories = async () => {
    try {
      const response = await fetch('/api/v1/catalog/categories');
      if (response.ok) {
        const data = await response.json();
        // Защита от получения объекта вместо массива категорий
        if (Array.isArray(data)) {
          setCategories(data);
        } else if (data && Array.isArray(data.categories)) {
          setCategories(data.categories);
        } else if (data && Array.isArray(data.data)) {
          setCategories(data.data);
        }
      }
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
    }
  };

  // 📥 2. Загрузка товаров с авто-распаковкой структур бэкенда
  const loadProducts = async () => {
    try {
      const response = await fetch('/api/v1/catalog/debug-db-raw-product');
      if (response.ok) {
        const data = await response.json();
        
        // 🔥 Умный маппинг структуры ответа бэкенда
        if (Array.isArray(data)) {
          setProducts(data);
        } else if (data && Array.isArray(data.products)) {
          setProducts(data.products);
        } else if (data && Array.isArray(data.data)) {
          setProducts(data.data);
        } else {
          setProducts([]);
        }
      }
    } catch (error) {
      console.error('Ошибка loading products:', error);
      setProducts([]);
    }
  };

  useEffect(() => {
    loadCategories();
    loadProducts();
  }, []);

  // 🔍 3. Логика Умного Поиска (Интеграция с GET /api/v1/catalog/search)
  useEffect(() => {
    if (!searchQuery) {
      loadProducts();
      return;
    }

    const delayDebounceFn = setTimeout(async () => {
      try {
        const response = await fetch(`/api/v1/catalog/search?q=${encodeURIComponent(searchQuery)}`);
        if (response.ok) {
          const data = await response.json();
          
          // 🔥 Защита от объекта в результатах поиска
          if (Array.isArray(data)) {
            setProducts(data);
          } else if (data && Array.isArray(data.products)) {
            setProducts(data.products);
          } else if (data && Array.isArray(data.data)) {
            setProducts(data.data);
          }
        }
      } catch (error) {
        console.error('Ошибка умного поиска:', error);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  // 🛠️ 4. Категорийный CRUD
  const handleCreateCategory = async () => {
    const name = prompt('Введите название новой категории:');
    if (!name) return;
    try {
      const response = await fetch('/api/v1/catalog/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, parent_id: selectedCategoryId })
      });
      if (response.ok) loadCategories();
    } catch (error) {
      console.error(error);
    }
  };

  const handleEditCategory = async (id: number) => {
    const cat = categories.find(c => c.id === id);
    const name = prompt('Редактировать название категории:', cat?.name);
    if (!name) return;
    try {
      await fetch(`/api/v1/catalog/categories/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, parent_id: cat?.parent_id || null })
      });
      loadCategories();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (!confirm('Удалить эту категорию?')) return;
    try {
      await fetch(`/api/v1/catalog/categories/${id}`, { method: 'DELETE' });
      loadCategories();
      if (selectedCategoryId === id) setSelectedCategoryId(null);
    } catch (error) {
      console.error(error);
    }
  };

  // 🛠️ 5. Товарный CRUD
  const handleCreateProduct = async () => {
    if (!selectedCategoryId) {
      alert('Сначала выберите категорию в дереве слева!');
      return;
    }
    const name = prompt('Название товара:');
    const code = prompt('Артикул товара:');
    const priceStr = prompt('Розничная цена:');
    if (!name || !code || !priceStr) return;

    try {
      await fetch('/api/v1/catalog/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          code,
          recommended_retail_price: parseFloat(priceStr),
          category_id: selectedCategoryId
        })
      });
      loadProducts();
    } catch (error) {
      console.error(error);
    }
  };

  const handleEditProduct = async (id: number) => {
    const prod = products.find(p => p.id === id);
    if (!prod) return;
    const name = prompt('Изменить название:', prod.name);
    const priceStr = prompt('Изменить цену:', prod.recommended_retail_price.toString());
    if (!name || !priceStr) return;

    try {
      await fetch(`/api/v1/catalog/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          recommended_retail_price: parseFloat(priceStr),
          category_id: prod.category_id
        })
      });
      loadProducts();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (!confirm('Удалить эту товарную карточку?')) return;
    try {
      await fetch(`/api/v1/catalog/products/${id}`, { method: 'DELETE' });
      loadProducts();
    } catch (error) {
      console.error(error);
    }
  };

  // 🔥 БЕЗОПАСНАЯ ФИЛЬТРАЦИЯ: Страница больше никогда не выдаст TypeError
  const filteredProducts = Array.isArray(products)
    ? products.filter(prod => {
        return searchQuery ? true : (selectedCategoryId ? prod.category_id === selectedCategoryId : true);
      })
    : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 60px)' }}>
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

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <CategoryTree
          categories={categories}
          selectedCategoryId={selectedCategoryId}
          onSelectCategory={(id) => setSelectedCategoryId(id)}
          onCreateCategory={handleCreateCategory}
          onEditCategory={handleEditCategory}
          onDeleteCategory={handleDeleteCategory}
        />
        
        <ProductGrid
          products={filteredProducts}
          onCreateProduct={handleCreateProduct}
          onEditProduct={handleEditProduct}
          onDeleteProduct={handleDeleteProduct}
        />
      </div>
    </div>
  );
};