// frontend/src/pages/admin/Catalog.tsx
import React, { useState, useEffect } from 'react';
import { CategoryTree } from '../../components/atomic/CategoryTree';
import { ProductGrid } from '../../components/atomic/ProductGrid';
import { BrandCreateModal } from '../../components/atomic/BrandCreateModal';

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

interface Brand {
  id: number;
  name: string;
}

export const Catalog: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showBrandModal, setShowBrandModal] = useState(false);

  const [newProdName, setNewProdName] = useState('');
  const [newProdCode, setNewProdCode] = useState('');
  const [newProdPrice, setNewProdPrice] = useState('');
  const [newProdBrandId, setNewProdBrandId] = useState('');
  const [newProdAliases, setNewProdAliases] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const getCategoryPath = (catId: number | null): string => {
    if (!catId) return 'Корень каталога';
    const path: string[] = [];
    let currentId: number | null = catId;
    while (currentId) {
      const cat = categories.find((c) => c.id === currentId);
      if (!cat) break;
      path.unshift(cat.name.replace(/_/g, ' '));
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
      }
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
    }
  };

  const loadProducts = async () => {
  try {
    const url = searchQuery
      ? `/api/v1/catalog/search?q=${encodeURIComponent(searchQuery)}`
      : '/api/v1/catalog/products/all';
    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      setProducts(Array.isArray(data) ? data : []);
    }
  } catch (error) {
    console.error('Ошибка загрузки товаров:', error);
  }
};

  const loadBrands = async () => {
    try {
      const response = await fetch('/api/v1/catalog/brands');
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) setBrands(data);
      }
    } catch (error) {
      console.error('Ошибка загрузки брендов:', error);
    }
  };

  useEffect(() => {
    loadCategories();
    loadBrands();
  }, []);

  useEffect(() => {
    loadProducts();
  }, [searchQuery]);

  const handleCreateCategory = async () => {
    const name = prompt(`Название новой категории внутри: ${getCategoryPath(selectedCategoryId)}`);
    if (!name) return;
    try {
      await fetch('/api/v1/catalog/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), parent_id: selectedCategoryId }),
      });
      loadCategories();
    } catch (e) {
      console.error(e);
    }
  };

  const handleEditCategory = async (id: number) => {
    const cat = categories.find((c) => c.id === id);
    const name = prompt('Новое название категории:', cat?.name);
    if (!name) return;
    try {
      await fetch(`/api/v1/catalog/categories/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), parent_id: cat?.parent_id || null }),
      });
      loadCategories();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (!confirm('Удалить категорию?')) return;
    try {
      const response = await fetch(`/api/v1/catalog/categories/${id}`, { method: 'DELETE' });
      if (response.ok) {
        loadCategories();
        if (selectedCategoryId === id) setSelectedCategoryId(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    if (!selectedCategoryId) {
      setFormError('Выберите категорию в дереве слева');
      return;
    }
    if (!newProdName || !newProdCode || !newProdBrandId) {
      setFormError('Название, Артикул и Бренд обязательны');
      return;
    }

    try {
      const response = await fetch('/api/v1/catalog/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newProdName.trim(),
          code: newProdCode.trim(),
          recommended_retail_price: newProdPrice ? parseFloat(newProdPrice) : 0.0,
          brand_id: parseInt(newProdBrandId),
          category_id: selectedCategoryId,
          search_aliases: newProdAliases
            ? newProdAliases.split(',').map((s) => s.trim()).filter(Boolean)
            : [],
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setFormSuccess('Товар создан');
        setNewProdName('');
        setNewProdCode('');
        setNewProdPrice('');
        setNewProdBrandId('');
        setNewProdAliases('');
        loadProducts();
        setTimeout(() => {
          setFormSuccess(null);
          setShowForm(false);
        }, 800);
      } else {
        setFormError(data.detail || 'Ошибка');
      }
    } catch (error) {
      setFormError('Ошибка сети');
    }
  };

  const handleEditProduct = async (id: number) => {
    const prod = products.find((p) => p.id === id);
    if (!prod) return;
    const name = prompt('Новое название:', prod.name);
    const price = prompt('Новая цена:', prod.recommended_retail_price?.toString());
    if (!name || !price) return;
    try {
      await fetch(`/api/v1/catalog/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), recommended_retail_price: parseFloat(price), category_id: prod.category_id }),
      });
      loadProducts();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (!confirm('Удалить товар?')) return;
    try {
      await fetch(`/api/v1/catalog/products/${id}`, { method: 'DELETE' });
      loadProducts();
    } catch (e) {
      console.error(e);
    }
  };

  const filteredProducts = products.filter((prod) =>
    selectedCategoryId ? prod.category_id === selectedCategoryId : true
  );

  return (
    <div className="page-content">
      {/* Верхняя панель */}
      <div className="card mb-3">
        <div className="d-flex justify-between align-center">
          <input
            type="text"
            placeholder="Поиск по названию или артикулу..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="form-control"
            style={{ maxWidth: '400px' }}
          />
          <div className="d-flex align-center gap-12">
            <span className="text-muted" style={{ fontWeight: 500 }}>
              📂 {getCategoryPath(selectedCategoryId)}
            </span>
            <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
              {showForm ? 'Скрыть' : '+ Добавить товар'}
            </button>
          </div>
        </div>
      </div>

      {/* Сворачиваемая форма */}
      {showForm && (
        <div className="card mb-3">
          <form onSubmit={handleCreateProduct}>
            <div className="form-row mb-2">
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Название *</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ключ рожковый 10мм"
                  value={newProdName}
                  onChange={(e) => setNewProdName(e.target.value)}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Артикул *</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="KEY-10-01"
                  value={newProdCode}
                  onChange={(e) => setNewProdCode(e.target.value)}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Цена</label>
                <input
                  type="number"
                  className="form-control"
                  placeholder="0.00"
                  step="0.01"
                  value={newProdPrice}
                  onChange={(e) => setNewProdPrice(e.target.value)}
                  style={{ width: '110px' }}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Бренд *</label>
                <div className="d-flex gap-8">
                  <select
                    className="form-control"
                    value={newProdBrandId}
                    onChange={(e) => setNewProdBrandId(e.target.value)}
                    style={{ width: '160px' }}
                  >
                    <option value="">-- Бренд --</option>
                    {brands.map((b) => (
                      <option key={b.id} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="btn btn-outline btn-sm"
                    onClick={() => setShowBrandModal(true)}
                    title="Добавить новый бренд"
                  >
                    +
                  </button>
                </div>
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Синонимы</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="десятка, ключ 10"
                  value={newProdAliases}
                  onChange={(e) => setNewProdAliases(e.target.value)}
                  style={{ width: '180px' }}
                />
              </div>
            </div>

            {formError && <div className="alert alert-danger" style={{ marginBottom: '8px', padding: '8px 12px' }}>{formError}</div>}
            {formSuccess && <div className="alert alert-success" style={{ marginBottom: '8px', padding: '8px 12px' }}>{formSuccess}</div>}

            <div className="d-flex gap-8">
              <button type="submit" className="btn btn-success btn-sm">Сохранить</button>
              <button type="button" className="btn btn-outline btn-sm" onClick={() => { setShowForm(false); setFormError(null); }}>
                Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Модальное окно: Новый бренд */}
      {showBrandModal && (
        <BrandCreateModal
          onClose={() => setShowBrandModal(false)}
          onBrandCreated={(brandId) => {
            loadBrands();
            setNewProdBrandId(String(brandId));
          }}
        />
      )}

      {/* Дерево + Сетка */}
      <div className="d-flex gap-16" style={{ alignItems: 'flex-start' }}>
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
          onCreateProduct={() => setShowForm(true)}
          onEditProduct={handleEditProduct}
          onDeleteProduct={handleDeleteProduct}
        />
      </div>
    </div>
  );
};