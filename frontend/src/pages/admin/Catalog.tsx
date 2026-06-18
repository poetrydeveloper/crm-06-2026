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

  // 🗺️ Построить цепочку родителей для выбранной категории
  const getCategoryPath = (catId: number | null): string => {
    if (!catId) return 'Корень каталога';
    const path: string[] = [];
    let currentId: number | null = catId;
    while (currentId) {
      const cat = categories.find(c => c.id === currentId);
      if (!cat) break;
      path.unshift(cat.name);
      currentId = cat.parent_id;
    }
    return path.join(' → ');
  };

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/v1/catalog/categories');
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) setCategories(data);
        else if (data?.categories) setCategories(data.categories);
        else if (data?.data) setCategories(data.data);
      }
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
    }
  };

  const loadProducts = async () => {
    try {
      const response = await fetch('/api/v1/catalog/debug-db-raw-product');
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) setProducts(data);
        else if (data?.products) setProducts(data.products);
        else if (data?.data) setProducts(data.data);
        else setProducts([]);
      }
    } catch (error) {
      console.error('Ошибка загрузки товаров:', error);
      setProducts([]);
    }
  };

  useEffect(() => {
    loadCategories();
    loadProducts();
  }, []);

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
          if (Array.isArray(data)) setProducts(data);
          else if (data?.products) setProducts(data.products);
          else if (data?.data) setProducts(data.data);
        }
      } catch (error) {
        console.error('Ошибка умного поиска:', error);
      }
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  // 🛠️ Категорийный CRUD
  const handleCreateCategory = async () => {
    const path = getCategoryPath(selectedCategoryId);
    const name = prompt(`📂 Место: ${path}\n\nВведите название новой категории:`);
    if (!name) return;
    try {
      const response = await fetch('/api/v1/catalog/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), parent_id: selectedCategoryId })
      });
      const data = await response.json();
      if (response.ok) {
        loadCategories();
      } else {
        alert(data.detail || 'Ошибка создания категории');
      }
    } catch (error) {
      console.error(error);
      alert('Ошибка сети при создании категории');
    }
  };

  const handleEditCategory = async (id: number) => {
    const cat = categories.find(c => c.id === id);
    const name = prompt('Редактировать название категории:', cat?.name);
    if (!name) return;
    try {
      const response = await fetch(`/api/v1/catalog/categories/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), parent_id: cat?.parent_id || null })
      });
      const data = await response.json();
      if (response.ok) {
        loadCategories();
      } else {
        alert(data.detail || 'Ошибка редактирования категории');
      }
    } catch (error) {
      console.error(error);
      alert('Ошибка сети');
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (!confirm('Удалить эту категорию?')) return;
    try {
      const response = await fetch(`/api/v1/catalog/categories/${id}`, { method: 'DELETE' });
      const data = await response.json();
      if (response.ok) {
        loadCategories();
        if (selectedCategoryId === id) setSelectedCategoryId(null);
      } else {
        alert(data.detail || 'Ошибка удаления категории');
      }
    } catch (error) {
      console.error(error);
      alert('Ошибка сети');
    }
  };

  // 🛠️ Товарный CRUD
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
      const response = await fetch('/api/v1/catalog/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          code: code.trim(),
          recommended_retail_price: parseFloat(priceStr),
          category_id: selectedCategoryId
        })
      });
      const data = await response.json();
      if (response.ok) {
        loadProducts();
      } else {
        alert(data.detail || 'Ошибка создания товара');
      }
    } catch (error) {
      console.error(error);
      alert('Ошибка сети');
    }
  };

  const handleEditProduct = async (id: number) => {
    const prod = products.find(p => p.id === id);
    if (!prod) return;
    const name = prompt('Изменить название:', prod.name);
    const priceStr = prompt('Изменить цену:', prod.recommended_retail_price.toString());
    if (!name || !priceStr) return;

    try {
      const response = await fetch(`/api/v1/catalog/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          recommended_retail_price: parseFloat(priceStr),
          category_id: prod.category_id
        })
      });
      const data = await response.json();
      if (response.ok) {
        loadProducts();
      } else {
        alert(data.detail || 'Ошибка редактирования товара');
      }
    } catch (error) {
      console.error(error);
      alert('Ошибка сети');
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (!confirm('Удалить эту товарную карточку?')) return;
    try {
      await fetch(`/api/v1/catalog/products/${id}`, { method: 'DELETE' });
      loadProducts();
    } catch (error) {
      console.error(error);
      alert('Ошибка сети');
    }
  };

  const filteredProducts = Array.isArray(products)
    ? products.filter(prod => searchQuery ? true : (selectedCategoryId ? prod.category_id === selectedCategoryId : true))
    : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 60px)' }}>
      <div style={{ background: '#1a1a1a', padding: '10px 20px', borderBottom: '1px solid #333', display: 'flex', alignItems: 'center', gap: '15px' }}>
        <input
          type="text"
          placeholder="🔍 Умный поиск товаров по названию или артикулу..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            flex: 1,
            maxWidth: '500px',
            padding: '8px 12px',
            borderRadius: '4px',
            border: '1px solid #444',
            background: '#2d2d2d',
            color: '#fff',
            outline: 'none'
          }}
        />
        {/* 🗺️ Показывает текущий путь */}
        <span style={{ color: '#888', fontSize: '13px' }}>
          📂 {getCategoryPath(selectedCategoryId)}
        </span>
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