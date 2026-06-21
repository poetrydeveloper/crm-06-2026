// frontend/src/components/atomic/CashboxShowcase.tsx
import React, { useState } from 'react';
import { UnitDetailView } from './UnitDetailView';

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
  available_qty: number;
}

interface UnitItem {
  unit_id: number;
  unique_serial_number: string;
  purchase_price: number;
  physical_status: string;
}

interface CategoryProduct {
  product_id: number;
  product_name: string;
  product_code: string;
  recommended_retail_price: number;
  in_stock: number;
  units: UnitItem[];
}

interface CashboxShowcaseProps {
  products: Product[];
  categoryUnits?: CategoryProduct[];
  onAddToCart: (product: Product) => void;
  onDisassembly?: (unitSerial: string, productId: number, mode: 'templated' | 'partial') => void;
  onAbsorb?: (unitIds: number[]) => void;
}

export const CashboxShowcase: React.FC<CashboxShowcaseProps> = ({
  products,
  categoryUnits,
  onAddToCart,
  onDisassembly,
  onAbsorb,
}) => {
  const [detailProductId, setDetailProductId] = useState<number | null>(null);

  // Режим категории
  if (categoryUnits && categoryUnits.length > 0) {
    // Детальный вид одного товара
    if (detailProductId !== null) {
      const cp = categoryUnits.find((c) => c.product_id === detailProductId);
      if (!cp) {
        setDetailProductId(null);
        return null;
      }

      return (
        <UnitDetailView
          product={cp}
          onBack={() => setDetailProductId(null)}
          onAddToCart={() =>
            onAddToCart({
              id: cp.product_id,
              name: cp.product_name,
              code: cp.product_code,
              recommended_retail_price: cp.recommended_retail_price,
              available_qty: cp.in_stock,
            })
          }
          onDisassembly={onDisassembly}
          onAbsorb={onAbsorb}
        />
      );
    }

    // Список карточек
    return (
      <div>
        <h3 className="card-title mb-3">Товары категории</h3>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
            gap: '12px',
          }}
        >
          {categoryUnits.map((cp) => (
            <div key={cp.product_id} className="card" style={{ padding: '14px' }}>
              <div className="d-flex justify-between align-center mb-2">
                <span
                  className={`badge ${cp.in_stock > 0 ? 'badge-success' : 'badge-danger'}`}
                  style={{ fontSize: '14px', padding: '4px 10px' }}
                >
                  {cp.in_stock} шт.
                </span>
              </div>
              <h4
                style={{
                  margin: '0 0 4px 0',
                  fontSize: '14px',
                  fontWeight: 600,
                  textTransform: 'capitalize',
                }}
              >
                {cp.product_name.replace(/_/g, ' ')}
              </h4>
              <div className="text-muted text-mono" style={{ fontSize: '11px', marginBottom: '8px' }}>
                {cp.product_code}
              </div>
              <div style={{ fontWeight: 700, fontSize: '16px', color: 'var(--text)', marginBottom: '8px' }}>
                {cp.recommended_retail_price.toFixed(2)} ₽
              </div>
              <div className="d-flex gap-4">
                <button
                  className="btn btn-success btn-sm"
                  disabled={cp.in_stock === 0}
                  onClick={() =>
                    onAddToCart({
                      id: cp.product_id,
                      name: cp.product_name,
                      code: cp.product_code,
                      recommended_retail_price: cp.recommended_retail_price,
                      available_qty: cp.in_stock,
                    })
                  }
                >
                  В чек
                </button>
                {cp.units.length > 0 && (
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => setDetailProductId(cp.product_id)}
                  >
                    Подробнее
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Режим поиска: показываем продукты
  if (products.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted">Введите запрос для поиска товаров</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="card-title mb-3">Результаты поиска</h3>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
          gap: '12px',
        }}
      >
        {products.map((product) => (
          <div key={product.id} className="card" style={{ padding: '14px' }}>
            <div className="d-flex justify-between align-center mb-2">
              <span
                className={`badge ${product.available_qty > 0 ? 'badge-success' : 'badge-danger'}`}
              >
                {product.available_qty} шт.
              </span>
            </div>
            <h4
              style={{
                margin: '0 0 4px 0',
                fontSize: '14px',
                fontWeight: 600,
                textTransform: 'capitalize',
              }}
            >
              {product.name.replace(/_/g, ' ')}
            </h4>
            <div className="text-muted text-mono" style={{ fontSize: '11px', marginBottom: '8px' }}>
              {product.code}
            </div>
            <div style={{ fontWeight: 700, fontSize: '16px', color: 'var(--text)', marginBottom: '8px' }}>
              {product.recommended_retail_price.toFixed(2)} ₽
            </div>
            <button
              className="btn btn-success btn-sm"
              disabled={product.available_qty === 0}
              onClick={() => onAddToCart(product)}
            >
              В чек
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};