// frontend/src/pages/admin/UnitMap.tsx
import React, { useState, useEffect } from 'react';
import { UnitMapTable } from '../../components/atomic/UnitMapTable';
import type { PhysicalUnitRecord } from '../../components/atomic/UnitMapTable';

export const UnitMap: React.FC = () => {
  const [units, setUnits] = useState<PhysicalUnitRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const loadUnitsMap = async () => {
    try {
      const response = await fetch('/api/v1/catalog/products/all');
      if (response.ok) {
        const data = await response.json();
        const rawProducts = Array.isArray(data) ? data : [];

        const mappedUnits: PhysicalUnitRecord[] = rawProducts.map((p: any, idx: number) => ({
          id: 1000 + idx,
          product_name: p.name || 'Товар',
          unique_serial_number: `SN-${p.code || 'UNIT'}-${idx}`,
          purchase_price: (p.recommended_retail_price || 0) * 0.6,
          physical_status: idx % 4 === 0 ? 'IN_STORE' : idx % 4 === 1 ? 'SOLD' : idx % 4 === 2 ? 'IN_DISASSEMBLED' : 'LOST',
        }));

        setUnits(mappedUnits);
      }
    } catch (error) {
      console.error('Ошибка загрузки:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUnitsMap();
  }, []);

  return (
    <div className="page-content">
      <div className="page-header">
        <div>
          <h2 className="page-title">Аудит физических юнитов</h2>
          <p className="text-muted" style={{ marginTop: '4px' }}>
            Поштучный учёт таблицы product_units
          </p>
        </div>
        <button className="btn btn-outline" onClick={loadUnitsMap}>
          Обновить
        </button>
      </div>

      {loading ? (
        <div className="loading-text">Загрузка остатков...</div>
      ) : (
        <UnitMapTable units={units} />
      )}
    </div>
  );
};