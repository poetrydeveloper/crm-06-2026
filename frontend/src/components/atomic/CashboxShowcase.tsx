// frontend/src/components/atomic/CashboxShowcase.tsx
import React from 'react';

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
  available_qty: number;
}

interface CashboxShowcaseProps {
  products: Product[];
  onAddToCart: (product: Product) => void;
}

export const CashboxShowcase: React.FC<CashboxShowcaseProps> = ({ products, onAddToCart }) => {
  if (products.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted">Введите запрос для поиска товаров</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="card-title">Результаты поиска</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
        {products.map((product) => (
          <div
            key={product.id}
            style={{
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              padding: '12px',
              background: 'var(--bg)',
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px', textTransform: 'capitalize' }}>
              {product.name.replace(/_/g, ' ')}
            </div>
            <div className="text-muted text-mono" style={{ fontSize: '12px', marginBottom: '8px' }}>
              {product.code}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
              В наличии: {product.available_qty} шт.
            </div>
            <div className="d-flex justify-between align-center">
              <span style={{ fontWeight: 700, fontSize: '16px', color: 'var(--primary)' }}>
                {product.recommended_retail_price.toFixed(2)} ₽
              </span>
              <button className="btn btn-success btn-sm" onClick={() => onAddToCart(product)}>
                В чек
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};