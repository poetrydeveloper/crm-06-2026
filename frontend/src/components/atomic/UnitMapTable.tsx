// frontend/src/components/atomic/UnitMapTable.tsx
import React from 'react';

export interface PhysicalUnitRecord {
  id: number;
  product_name: string;
  unique_serial_number: string;
  purchase_price: number;
  physical_status: 'IN_STORE' | 'SOLD' | 'LOST' | 'IN_DISASSEMBLED' | 'ABSORBED';
}

interface UnitMapTableProps {
  units: PhysicalUnitRecord[];
}

const statusMap: Record<string, string> = {
  IN_STORE: 'badge-success',
  SOLD: 'badge-secondary',
  IN_DISASSEMBLED: 'badge-warning',
  ABSORBED: 'badge-info',
  LOST: 'badge-danger',
};

export const UnitMapTable: React.FC<UnitMapTableProps> = ({ units }) => {
  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Товар</th>
            <th>Серийный номер</th>
            <th>Себестоимость</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {units.length === 0 ? (
            <tr>
              <td colSpan={5} className="empty-row">Нет зарегистрированных юнитов</td>
            </tr>
          ) : (
            units.map((unit) => (
              <tr key={unit.id}>
                <td className="text-muted">#{unit.id}</td>
                <td style={{ fontWeight: 500 }}>{unit.product_name}</td>
                <td className="text-mono" style={{ color: 'var(--primary)' }}>{unit.unique_serial_number}</td>
                <td style={{ color: 'var(--success)', fontWeight: 600 }}>{unit.purchase_price.toFixed(2)} ₽</td>
                <td>
                  <span className={`badge ${statusMap[unit.physical_status] || 'badge-secondary'}`}>
                    {unit.physical_status}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};