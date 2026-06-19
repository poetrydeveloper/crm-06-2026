// frontend/src/pages/admin/UnitMap.tsx
import React, { useState, useEffect } from 'react';

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
  recommended_retail_price: number;
  in_stock: number;
}

export const UnitMap: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<ProductWithStock[]>([]);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState<Set<number>>(new Set());

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/v1/catalog/categories');
      if (response.ok) {
        const data = await response.json();
        setCategories(Array.isArray(data) ? data : []);
      }
    } catch (e) {
      console.error('Ошибка загрузки категорий:', e);
    }
  };

  const loadProductsWithStock = async () => {
    try {
      const response = await fetch('/api/v1/catalog/products/all');
      if (response.ok) {
        const data = await response.json();

        const enriched: ProductWithStock[] = [];
        for (const p of data) {
          try {
            const searchRes = await fetch(`/api/v1/catalog/search?q=${encodeURIComponent(p.code)}`);
            if (searchRes.ok) {
              const searchData = await searchRes.json();
              const match = searchData.find((s: any) => s.id === p.id);
              enriched.push({ ...p, in_stock: match?.available_qty || 0 });
            } else {
              enriched.push({ ...p, in_stock: 0 });
            }
          } catch {
            enriched.push({ ...p, in_stock: 0 });
          }
        }
        setProducts(enriched);
      }
    } catch (e) {
      console.error('Ошибка загрузки товаров:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
    loadProductsWithStock();
  }, []);

  const toggleCategory = (id: number) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const getStockClass = (qty: number): string => {
    if (qty === 0) return 'stock-zero';
    if (qty >= 3) return 'stock-good';
    return 'stock-low';
  };

  const renderCategory = (cat: Category, depth: number): React.ReactNode => {
    const children = categories.filter((c) => c.parent_id === cat.id);
    const catProducts = products.filter((p) => p.category_id === cat.id);
    const totalStock = catProducts.reduce((s, p) => s + p.in_stock, 0);
    const hasChildren = children.length > 0;
    const isCollapsed = collapsed.has(cat.id);
    const indent = depth * 20;

    return (
      <div key={cat.id}>
        <div
          className="category-header"
          style={{ paddingLeft: `${indent}px` }}
        >
          <div
            className="category-row-clickable"
            onClick={() => hasChildren && toggleCategory(cat.id)}
          >
            <span className="category-arrow">
              {hasChildren ? (isCollapsed ? '►' : '▼') : ''}
            </span>
            <span className="category-name">
              {cat.name.replace(/_/g, ' ')}
            </span>
            <span className={`category-badge ${getStockClass(totalStock)}`}>
              {totalStock} шт.
            </span>
          </div>

          {!isCollapsed && catProducts.length > 0 && (
            <div className="category-products-grid">
              {catProducts.map((p) => (
                <div key={p.id} className={`unit-mini-card ${getStockClass(p.in_stock)}`}>
                  <div className="unit-mini-name">{p.name.replace(/_/g, ' ')}</div>
                  <div className="unit-mini-code">{p.code}</div>
                  <div className="unit-mini-qty">
                    {p.in_stock}
                    <span>шт.</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {!isCollapsed && hasChildren && (
          <div>
            {children.map((child) => renderCategory(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const rootCategories = categories.filter((c) => !c.parent_id);

  return (
    <div className="page-content">
      <style>{`
        .category-header {
          margin-bottom: 2px;
        }
        .category-row-clickable {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          cursor: pointer;
          border-radius: var(--radius-sm);
          transition: background 0.1s;
          user-select: none;
          border-left: 3px solid transparent;
        }
        .category-row-clickable:hover {
          background: var(--bg-secondary);
        }
        .category-arrow {
          width: 16px;
          font-size: 11px;
          color: var(--text-muted);
          flex-shrink: 0;
        }
        .category-name {
          font-weight: 600;
          font-size: 14px;
          flex: 1;
        }
        .category-badge {
          font-size: 12px;
          font-weight: 600;
          padding: 2px 10px;
          border-radius: 10px;
          flex-shrink: 0;
        }
        .category-badge.stock-zero {
          background: #fdd;
          color: #a00;
        }
        .category-badge.stock-low {
          background: #fff3cd;
          color: #856404;
        }
        .category-badge.stock-good {
          background: #d4edda;
          color: #155724;
        }
        .category-products-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 8px;
          padding: 8px 0 12px 36px;
        }
        .unit-mini-card {
          padding: 10px 12px;
          border-radius: var(--radius-sm);
          border: 1px solid rgba(0,0,0,0.06);
        }
        .unit-mini-card.stock-zero {
          background: #fff0f0;
          color: #a00;
        }
        .unit-mini-card.stock-low {
          background: #fffef0;
          color: #856404;
        }
        .unit-mini-card.stock-good {
          background: #f0fff4;
          color: #155724;
        }
        .unit-mini-name {
          font-weight: 600;
          font-size: 13px;
          text-transform: capitalize;
          margin-bottom: 3px;
        }
        .unit-mini-code {
          font-family: var(--font-mono);
          font-size: 11px;
          opacity: 0.7;
          margin-bottom: 6px;
        }
        .unit-mini-qty {
          font-size: 22px;
          font-weight: 700;
        }
        .unit-mini-qty span {
          font-size: 12px;
          font-weight: 400;
          margin-left: 3px;
        }
      `}</style>

      <div className="page-header">
        <div>
          <h2 className="page-title">Остатки по категориям</h2>
          <p className="text-muted" style={{ marginTop: '4px' }}>
            🔴 0 шт. &nbsp; 🟡 1-2 шт. &nbsp; 🟢 3+ шт.
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