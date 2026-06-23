// frontend/src/components/atomic/CashboxShowcase.tsx
import React, { useState } from 'react';
import { UnitDetailView } from './UnitDetailView';

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
  available_qty: number;
  category_id?: number;
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
  in_store_qty?: number;
  disassembled_qty?: number;
  units: UnitItem[];
}

interface CashboxShowcaseProps {
  products: Product[];
  categoryUnits?: CategoryProduct[];
  onAddToCart: (product: Product) => void;
  onSelectCategory?: (categoryId: number) => void;
  onDisassembly?: (unitSerial: string, productId: number, mode: 'templated' | 'partial') => void;
  onAbsorb?: (unitIds: number[]) => void;
  onReassemble?: (parentUnitId: number) => void;
}

export const CashboxShowcase: React.FC<CashboxShowcaseProps> = ({
  products,
  categoryUnits,
  onAddToCart,
  onSelectCategory,
  onDisassembly,
  onAbsorb,
  onReassemble,
}) => {
  const [detailProductId, setDetailProductId] = useState<number | null>(null);
  const [selectedPrices, setSelectedPrices] = useState<Record<number, number>>({});

  const groupByPrice = (units: UnitItem[]): Map<number, UnitItem[]> => {
    const map = new Map<number, UnitItem[]>();
    for (const u of units) {
      const key = u.purchase_price;
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(u);
    }
    return map;
  };

  const getDefaultPrice = (productId: number, priceGroups: Map<number, UnitItem[]>): number => {
    if (selectedPrices[productId] && priceGroups.has(selectedPrices[productId])) {
      return selectedPrices[productId];
    }
    const firstPrice = priceGroups.keys().next().value;
    if (firstPrice !== undefined) return firstPrice;
    return 0;
  };

  // Режим категории
  if (categoryUnits && categoryUnits.length > 0) {
    if (detailProductId !== null) {
      const cp = categoryUnits.find((c) => c.product_id === detailProductId);
      if (!cp) { setDetailProductId(null); return null; }

      const priceGroups = groupByPrice(cp.units);
      const selectedPrice = getDefaultPrice(cp.product_id, priceGroups);
      const filteredUnits = priceGroups.get(selectedPrice) || [];

      return (
        <UnitDetailView
          product={{ ...cp, units: filteredUnits, in_stock: filteredUnits.length }}
          onBack={() => setDetailProductId(null)}
          onAddToCart={() =>
            onAddToCart({
              id: cp.product_id,
              name: cp.product_name,
              code: cp.product_code,
              recommended_retail_price: selectedPrice,
              available_qty: filteredUnits.filter(u => u.physical_status === 'IN_STORE').length,
            })
          }
          onDisassembly={onDisassembly}
          onAbsorb={onAbsorb}
          onReassemble={onReassemble}
        />
      );
    }

    return (
      <div>
        <h3 className="card-title mb-3">Товары категории</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
          {categoryUnits.map((cp) => {
            const priceGroups = groupByPrice(cp.units);
            const selectedPrice = getDefaultPrice(cp.product_id, priceGroups);
            const totalStock = cp.in_stock;
            const inStore = cp.in_store_qty || 0;
            const disassembled = cp.disassembled_qty || 0;

            return (
              <div key={cp.product_id} className="card" style={{ padding: '14px' }}>
                <div className="d-flex justify-between align-center mb-2">
                  <div>
                    <span className={`badge ${totalStock > 0 ? 'badge-success' : 'badge-danger'}`} style={{ fontSize: '14px', padding: '4px 10px' }}>
                      {totalStock} шт.
                    </span>
                    {(inStore > 0 || disassembled > 0) && (
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '3px' }}>
                        {inStore > 0 && <span style={{ color: 'var(--success)' }}>{inStore} в наличии</span>}
                        {inStore > 0 && disassembled > 0 && ' • '}
                        {disassembled > 0 && <span style={{ color: 'var(--warning)', fontWeight: 600 }}>{disassembled} разобран</span>}
                      </div>
                    )}
                  </div>
                </div>
                <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: 600, textTransform: 'capitalize' }}>
                  {cp.product_name.replace(/_/g, ' ')}
                </h4>
                <div className="text-muted text-mono" style={{ fontSize: '11px', marginBottom: '6px' }}>{cp.product_code}</div>

                {/* Группировка по закупочным ценам */}
                <div style={{ marginBottom: '8px' }}>
                  <div className="text-muted" style={{ fontSize: '10px', fontWeight: 600, marginBottom: '3px' }}>Закупка:</div>
                  {Array.from(priceGroups.entries()).map(([price, units]) => {
                    const isSelected = price === selectedPrice;
                    const storeUnits = units.filter(u => u.physical_status === 'IN_STORE').length;
                    const disUnits = units.filter(u => u.physical_status === 'IN_DISASSEMBLED').length;
                    return (
                      <div
                        key={price}
                        onClick={() => setSelectedPrices(prev => ({ ...prev, [cp.product_id]: price }))}
                        style={{
                          cursor: 'pointer',
                          padding: '2px 0',
                          fontSize: '13px',
                          fontWeight: isSelected ? 700 : 400,
                          color: isSelected ? 'var(--primary)' : 'var(--text)',
                          textDecoration: isSelected ? 'underline' : 'none',
                        }}
                      >
                        {price.toFixed(2)} ₽ ({units.length} шт.)
                        {(disUnits > 0) && (
                          <span style={{ fontSize: '11px', color: 'var(--warning)', marginLeft: '4px' }}>
                            ({disUnits} разобр.)
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                <div className="d-flex gap-4">
                  {inStore > 0 && (
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() =>
                        onAddToCart({
                          id: cp.product_id,
                          name: cp.product_name,
                          code: cp.product_code,
                          recommended_retail_price: selectedPrice,
                          available_qty: inStore,
                        })
                      }
                    >
                      В чек
                    </button>
                  )}
                  {cp.units.length > 0 && (
                    <button className="btn btn-outline btn-sm" onClick={() => setDetailProductId(cp.product_id)}>
                      Подробнее
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Режим поиска
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
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
        {products.map((product) => (
          <div
            key={product.id}
            className="card"
            style={{ padding: '14px', cursor: onSelectCategory ? 'pointer' : 'default' }}
            onClick={() => onSelectCategory?.(product.category_id || 0)}
          >
            <div className="d-flex justify-between align-center mb-2">
              <span className={`badge ${product.available_qty > 0 ? 'badge-success' : 'badge-danger'}`}>
                {product.available_qty} шт.
              </span>
            </div>
            <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: 600, textTransform: 'capitalize' }}>
              {product.name.replace(/_/g, ' ')}
            </h4>
            <div className="text-muted text-mono" style={{ fontSize: '11px', marginBottom: '8px' }}>{product.code}</div>
            <div style={{ fontWeight: 700, fontSize: '16px', color: 'var(--text)' }}>
              {product.recommended_retail_price.toFixed(2)} ₽
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};