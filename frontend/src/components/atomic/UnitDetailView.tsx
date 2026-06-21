// frontend/src/components/atomic/UnitDetailView.tsx
import React, { useState } from 'react';

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

interface UnitDetailViewProps {
  product: CategoryProduct;
  onBack: () => void;
  onAddToCart: () => void;
  onDisassembly?: (unitSerial: string, productId: number, mode: 'templated' | 'partial') => void;
  onAbsorb?: (unitIds: number[]) => void;
}

export const UnitDetailView: React.FC<UnitDetailViewProps> = ({
  product,
  onBack,
  onAddToCart,
  onDisassembly,
  onAbsorb,
}) => {
  const [selectedForAbsorb, setSelectedForAbsorb] = useState<Set<number>>(new Set());
  const [showDisassemblyMenu, setShowDisassemblyMenu] = useState(false);

  const handleSelectForAbsorb = (unitId: number) => {
    setSelectedForAbsorb((prev) => {
      const next = new Set(prev);
      if (next.has(unitId)) next.delete(unitId);
      else next.add(unitId);
      return next;
    });
  };

  const absorbCount = selectedForAbsorb.size;
  const hasInStoreUnits = product.units.some((u) => u.physical_status === 'IN_STORE');

  return (
    <div>
      <button className="btn btn-outline btn-sm mb-3" onClick={onBack}>
        ← Назад к списку
      </button>

      <div className="card" style={{ padding: '20px' }}>
        {/* Заголовок */}
        <div className="d-flex justify-between align-start mb-3">
          <div>
            <h3 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: 600, textTransform: 'capitalize' }}>
              {product.product_name.replace(/_/g, ' ')}
            </h3>
            <div className="text-muted text-mono" style={{ fontSize: '13px' }}>{product.product_code}</div>
          </div>
          <span
            className={`badge ${product.in_stock > 0 ? 'badge-success' : 'badge-danger'}`}
            style={{ fontSize: '16px', padding: '6px 14px' }}
          >
            {product.in_stock} шт.
          </span>
        </div>

        <div style={{ fontWeight: 700, fontSize: '20px', marginBottom: '16px' }}>
          {product.recommended_retail_price.toFixed(2)} ₽ / шт.
        </div>

        {/* Таблица юнитов */}
        <div className="table-wrapper mb-3">
          <table className="table" style={{ fontSize: '13px' }}>
            <thead>
              <tr>
                {(onAbsorb || absorbCount > 0) && <th style={{ width: '30px' }}></th>}
                <th>Серийный номер</th>
                <th style={{ textAlign: 'right' }}>Закупочная цена</th>
                <th style={{ textAlign: 'center' }}>Статус</th>
              </tr>
            </thead>
            <tbody>
              {product.units.map((u) => (
                <tr
                  key={u.unit_id}
                  style={{ background: selectedForAbsorb.has(u.unit_id) ? 'var(--bg-secondary)' : undefined }}
                >
                  {(onAbsorb || absorbCount > 0) && (
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedForAbsorb.has(u.unit_id)}
                        onChange={() => handleSelectForAbsorb(u.unit_id)}
                      />
                    </td>
                  )}
                  <td className="text-mono" style={{ color: 'var(--primary)' }}>{u.unique_serial_number}</td>
                  <td style={{ textAlign: 'right', color: 'var(--success)', fontWeight: 500 }}>
                    {u.purchase_price.toFixed(2)} ₽
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={`badge ${u.physical_status === 'IN_STORE' ? 'badge-success' : 'badge-secondary'}`}>
                      {u.physical_status}
                    </span>
                  </td>
                </tr>
              ))}
              {product.units.length === 0 && (
                <tr>
                  <td colSpan={4} className="empty-row">Нет юнитов на складе</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Кнопки действий */}
        <div className="d-flex gap-8 flex-wrap">
          <button
            className="btn btn-success"
            disabled={product.in_stock === 0}
            onClick={onAddToCart}
          >
            Добавить в чек
          </button>

          {onDisassembly && hasInStoreUnits && (
            <div style={{ position: 'relative' }}>
              <button
                className="btn btn-outline"
                onClick={() => setShowDisassemblyMenu(!showDisassemblyMenu)}
              >
                Разобрать набор ▼
              </button>
              {showDisassemblyMenu && (
                <div
                  className="card"
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    zIndex: 100,
                    minWidth: '280px',
                    marginTop: '4px',
                    padding: '12px',
                  }}
                >
                  <p className="text-muted" style={{ fontSize: '12px', marginBottom: '8px' }}>
                    Выберите способ разбора:
                  </p>
                  <button
                    className="btn btn-outline btn-sm"
                    style={{ width: '100%', marginBottom: '4px', textAlign: 'left' }}
                    onClick={() => {
                      const firstUnit = product.units.find((u) => u.physical_status === 'IN_STORE');
                      if (firstUnit) onDisassembly(firstUnit.unique_serial_number, product.product_id, 'templated');
                      setShowDisassemblyMenu(false);
                    }}
                  >
                    📦 Вариант А: По шаблону
                  </button>
                  <button
                    className="btn btn-outline btn-sm"
                    style={{ width: '100%', textAlign: 'left' }}
                    onClick={() => {
                      const firstUnit = product.units.find((u) => u.physical_status === 'IN_STORE');
                      if (firstUnit) onDisassembly(firstUnit.unique_serial_number, product.product_id, 'partial');
                      setShowDisassemblyMenu(false);
                    }}
                  >
                    ⚡ Вариант В: Частичный (под клиента)
                  </button>
                </div>
              )}
            </div>
          )}

          {onAbsorb && absorbCount > 0 && (
            <button
              className="btn btn-primary"
              onClick={() => {
                const ids = product.units
                  .filter((u) => selectedForAbsorb.has(u.unit_id))
                  .map((u) => u.unit_id);
                onAbsorb(ids);
                setSelectedForAbsorb(new Set());
              }}
            >
              Собрать в набор ({absorbCount})
            </button>
          )}
        </div>
      </div>
    </div>
  );
};