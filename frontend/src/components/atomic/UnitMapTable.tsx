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

export const UnitMapTable: React.FC<UnitMapTableProps> = ({ units }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'IN_STORE': return { bg: '#1b5e20', text: '#a5d6a7' };     // На полке
      case 'SOLD': return { bg: '#2d2d2d', text: '#888' };          // Продан клиенту
      case 'IN_DISASSEMBLED': return { bg: '#e65100', text: '#ffb74d' }; // Разобран на сателлиты
      case 'ABSORBED': return { bg: '#1a237e', text: '#9fa8da' };    // Поглощен в сборку
      case 'LOST': return { bg: '#b71c1c', text: '#ff8a80' };        // Заморожен/Некомплект
      default: return { bg: '#222', text: '#fff' };
    }
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
        <thead>
          <tr style={{ background: '#222', borderBottom: '2px solid #333', textAlign: 'left', color: '#aaa' }}>
            <th style={{ padding: '12px' }}>ID Экземпляра</th>
            <th style={{ padding: '12px' }}>Номенклатура (Product)</th>
            <th style={{ padding: '12px' }}>Уникальный Серийный Номер (SN)</th>
            <th style={{ padding: '12px' }}>Цена Закупки (Себестоимость)</th>
            <th style={{ padding: '12px' }}>Физический Статус в СУБД</th>
          </tr>
        </thead>
        <tbody>
          {units.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ padding: '30px', textAlign: 'center', color: '#555' }}>
                📭 В СУБД пока нет зарегистрированных физических юнитов.
              </td>
            </tr>
          ) : (
            units.map(unit => {
              const colors = getStatusColor(unit.physical_status);
              return (
                <tr key={unit.id} style={{ 
                  borderBottom: '1px solid #2d2d2d',
                  background: unit.physical_status === 'SOLD' ? '#141414' : 'transparent'
                }}>
                  <td style={{ padding: '12px', fontWeight: 'bold', color: '#888' }}>#{unit.id}</td>
                  <td style={{ padding: '12px', fontWeight: '500' }}>{unit.product_name}</td>
                  <td style={{ padding: '12px', color: '#4fa8ff', fontFamily: 'monospace', fontWeight: 'bold' }}>{unit.unique_serial_number}</td>
                  <td style={{ padding: '12px', color: '#2ea44f' }}>{unit.purchase_price.toFixed(2)} ₽</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ 
                      background: colors.bg, 
                      color: colors.text,
                      padding: '4px 10px', 
                      borderRadius: '4px', 
                      fontSize: '12px', 
                      fontWeight: 'bold'
                    }}>
                      {unit.physical_status}
                    </span>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
};
