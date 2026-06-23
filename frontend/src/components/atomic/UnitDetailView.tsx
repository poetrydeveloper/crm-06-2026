// frontend/src/components/atomic/UnitDetailView.tsx
import React, { useState, useEffect } from 'react';

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

interface UnitDetailViewProps {
  product: CategoryProduct;
  onBack: () => void;
  onAddToCart: () => void;
  onDisassembly?: (unitSerial: string, productId: number, mode: 'templated' | 'partial') => void;
  onAbsorb?: (unitIds: number[]) => void;
  onReassemble?: (parentUnitId: number) => void;
}

export const UnitDetailView: React.FC<UnitDetailViewProps> = ({
  product,
  onBack,
  onAddToCart,
  onDisassembly,
  onAbsorb,
  onReassemble,
}) => {
  const [selectedForAbsorb, setSelectedForAbsorb] = useState<Set<number>>(new Set());
  const [showDisassemblyMenu, setShowDisassemblyMenu] = useState(false);
  const [satelliteIds, setSatelliteIds] = useState<number[]>([]);
  const [loadingSatellites, setLoadingSatellites] = useState(false);

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
  const disassembledUnit = product.units.find((u) => u.physical_status === 'IN_DISASSEMBLED');
  const hasDisassembled = !!disassembledUnit;

  // Загрузить сателлиты разобранного набора
  useEffect(() => {
    if (!disassembledUnit) return;
    setLoadingSatellites(true);
    fetch(`/api/v1/warehouse/units/${disassembledUnit.unit_id}/satellites`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.satellite_ids) setSatelliteIds(data.satellite_ids);
      })
      .catch(() => {})
      .finally(() => setLoadingSatellites(false));
  }, [disassembledUnit?.unit_id]);

  const handleReassemble = async () => {
    if (!disassembledUnit || satelliteIds.length === 0) return;
    try {
      const r = await fetch('/api/v1/warehouse/sets/absorb', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_product_id: product.product_id,
          satellite_unit_ids: satelliteIds,
        }),
      });
      if (r.ok) {
        alert('Набор собран обратно');
        onReassemble?.(disassembledUnit.unit_id);
        onBack();
      }
    } catch {}
  };

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
          <div className="d-flex gap-8">
            {product.disassembled_qty !== undefined && product.disassembled_qty > 0 && (
              <span className="badge badge-warning" style={{ fontSize: '14px', padding: '6px 14px' }}>
                Разобрано: {product.disassembled_qty}
              </span>
            )}
            <span
              className={`badge ${product.in_stock > 0 ? 'badge-success' : 'badge-danger'}`}
              style={{ fontSize: '14px', padding: '6px 14px' }}
            >
              В наличии: {product.in_stock} шт.
            </span>
          </div>
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
                      {u.physical_status === 'IN_STORE' && (
                        <input
                          type="checkbox"
                          checked={selectedForAbsorb.has(u.unit_id)}
                          onChange={() => handleSelectForAbsorb(u.unit_id)}
                        />
                      )}
                    </td>
                  )}
                  <td className="text-mono" style={{ color: 'var(--primary)' }}>{u.unique_serial_number}</td>
                  <td style={{ textAlign: 'right', color: 'var(--success)', fontWeight: 500 }}>
                    {u.purchase_price.toFixed(2)} ₽
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={`badge ${
                      u.physical_status === 'IN_STORE' ? 'badge-success' :
                      u.physical_status === 'IN_DISASSEMBLED' ? 'badge-warning' :
                      'badge-secondary'
                    }`}>
                      {u.physical_status === 'IN_DISASSEMBLED' ? 'РАЗОБРАН' : u.physical_status}
                    </span>
                  </td>
                </tr>
              ))}
              {product.units.length === 0 && (
                <tr>
                  <td colSpan={4} className="empty-row">Нет юнитов</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Кнопки действий */}
        <div className="d-flex gap-8 flex-wrap">
          {!hasDisassembled && (
            <button
              className="btn btn-success"
              disabled={product.in_stock === 0}
              onClick={onAddToCart}
            >
              Добавить в чек
            </button>
          )}

          {onDisassembly && hasInStoreUnits && (
            <div style={{ position: 'relative' }}>
              <button
                className="btn btn-outline"
                onClick={() => setShowDisassemblyMenu(!showDisassemblyMenu)}
              >
                Разобрать набор ▼
              </button>
              {showDisassemblyMenu && (
                <div className="card" style={{ position: 'absolute', top: '100%', left: 0, zIndex: 100, minWidth: '280px', marginTop: '4px', padding: '12px' }}>
                  <p className="text-muted" style={{ fontSize: '12px', marginBottom: '8px' }}>Выберите способ разбора:</p>
                  <button className="btn btn-outline btn-sm" style={{ width: '100%', marginBottom: '4px', textAlign: 'left' }}
                    onClick={() => {
                      const firstUnit = product.units.find((u) => u.physical_status === 'IN_STORE');
                      if (firstUnit) onDisassembly(firstUnit.unique_serial_number, product.product_id, 'templated');
                      setShowDisassemblyMenu(false);
                    }}>
                    📦 Вариант А: По шаблону
                  </button>
                  <button className="btn btn-outline btn-sm" style={{ width: '100%', textAlign: 'left' }}
                    onClick={() => {
                      const firstUnit = product.units.find((u) => u.physical_status === 'IN_STORE');
                      if (firstUnit) onDisassembly(firstUnit.unique_serial_number, product.product_id, 'partial');
                      setShowDisassemblyMenu(false);
                    }}>
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
                const ids = product.units.filter((u) => selectedForAbsorb.has(u.unit_id)).map((u) => u.unit_id);
                onAbsorb(ids);
                setSelectedForAbsorb(new Set());
              }}
            >
              Собрать в набор ({absorbCount})
            </button>
          )}

          {hasDisassembled && (
            <button
              className="btn btn-warning"
              disabled={loadingSatellites || satelliteIds.length === 0}
              onClick={handleReassemble}
            >
              {loadingSatellites ? 'Поиск сателлитов...' : `Собрать обратно (${satelliteIds.length} сателлитов)`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};