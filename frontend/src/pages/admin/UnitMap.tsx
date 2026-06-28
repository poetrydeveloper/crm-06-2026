// frontend/src/pages/admin/UnitMap.tsx
import React, { useState, useEffect } from 'react';
import { UnitMapCard } from '../../components/atomic/UnitMapCard';
import { UnitMapStyles } from './UnitMapStyles';

interface Category {
  id: number;
  name: string;
  parent_id: number | null;
}

interface ProductWithStock {
  id: number;
  name: string;
  code: string;
  category_id: number;
  brand_name: string;
  recommended_retail_price: number;
  in_stock: number;
  expected_qty: number;
  disassembled_qty: number;
}

export const UnitMap: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<ProductWithStock[]>([]);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState<Set<number>>(new Set());

  const loadCategories = async () => {
    try {
      const r = await fetch('/api/v1/catalog/categories');
      if (r.ok) setCategories(await r.json());
    } catch {}
  };

  const loadProductsWithStock = async () => {
    try {
      const r = await fetch('/api/v1/catalog/products/all');
      if (!r.ok) return;
      const data = await r.json();
      const enriched: ProductWithStock[] = [];
      for (const p of data) {
        try {
          const unitsRes = await fetch(`/api/v1/warehouse/units/by-category/${p.category_id}`);
          const unitsData = unitsRes.ok ? await unitsRes.json() : [];
          const catProd = unitsData.find((u: any) => u.product_id === p.id);
          enriched.push({
            ...p,
            brand_name: catProd?.brand_name || '',
            in_stock: catProd?.in_store_qty || 0,
            expected_qty: catProd?.expected_qty || 0,
            disassembled_qty: catProd?.disassembled_qty || 0,
          });
        } catch {
          enriched.push({
            ...p,
            brand_name: '',
            in_stock: 0,
            expected_qty: 0,
            disassembled_qty: 0,
          });
        }
      }
      setProducts(enriched);
    } catch {}
    setLoading(false);
  };

  useEffect(() => {
    loadCategories();
    loadProductsWithStock();
  }, []);

  const toggleCategory = (id: number) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const getStockClass = (qty: number): string =>
    qty === 0 ? 'badge-danger' : qty >= 3 ? 'badge-success' : 'badge-warning';

  const renderCategory = (cat: Category, depth: number): React.ReactNode => {
    const children = categories.filter((c) => c.parent_id === cat.id);
    const catProducts = products.filter((p) => p.category_id === cat.id);
    const totalStock = catProducts.reduce((s, p) => s + p.in_stock, 0);
    const totalExpected = catProducts.reduce((s, p) => s + p.expected_qty, 0);
    const isCollapsed = collapsed.has(cat.id);
    const indent = depth * 20;

    return (
      <div key={cat.id}>
        <div style={{ paddingLeft: `${indent}px` }}>
          <div
            className="category-row"
            onClick={() => children.length > 0 && toggleCategory(cat.id)}
          >
            <span className="category-arrow">
              {children.length > 0 ? (isCollapsed ? '►' : '▼') : ''}
            </span>
            <span className="category-name">{cat.name.replace(/_/g, ' ')}</span>
            <span className={`badge ${getStockClass(totalStock)}`}>{totalStock} шт.</span>
            {totalExpected > 0 && <span className="badge badge-info">{totalExpected} в пути</span>}
          </div>
          {!isCollapsed && catProducts.length > 0 && (
            <div className="products-grid">
              {catProducts.map((p) => (
                <UnitMapCard key={p.id} product={p} />
              ))}
            </div>
          )}
        </div>
        {!isCollapsed &&
          children.length > 0 &&
          children.map((child) => renderCategory(child, depth + 1))}
      </div>
    );
  };

  const rootCategories = categories.filter((c) => !c.parent_id);

  return (
    <div className="page-content">
      <UnitMapStyles />
      <div className="page-header">
        <div>
          <h2 className="page-title">Остатки по категориям</h2>
          <p className="text-muted" style={{ marginTop: '4px' }}>
            Верх — в заявке (EXPECTED) &nbsp;|&nbsp; Низ — на полке (IN_STORE)
          </p>
        </div>
        <button className="btn btn-outline" onClick={loadProductsWithStock}>
          Обновить
        </button>
      </div>
      {loading ? (
        <div className="loading-text">Загрузка остатков...</div>
      ) : (
        <div className="card">
          {rootCategories.length === 0 ? (
            <div className="text-muted text-center" style={{ padding: '40px' }}>
              Нет категорий
            </div>
          ) : (
            rootCategories.map((cat) => renderCategory(cat, 0))
          )}
        </div>
      )}
    </div>
  );
};
