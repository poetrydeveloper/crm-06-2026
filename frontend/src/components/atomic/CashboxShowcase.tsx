// frontend/src/components/atomic/CashboxShowcase.tsx
import React from 'react';

interface PhysicalUnit {
  id: number;
  name: string;
  code: string;
  unique_serial_number: string;
  recommended_retail_price: number;
  physical_status: 'IN_STORE' | 'SOLD' | 'LOST' | 'IN_DISASSEMBLED' | 'ABSORBED';
}

interface CashboxShowcaseProps {
  units: PhysicalUnit[];
  searchQuery: string;
  onAddToBag: (unit: PhysicalUnit) => void;
}

export const CashboxShowcase: React.FC<CashboxShowcaseProps> = ({
  units,
  searchQuery,
  onAddToBag,
}) => {
  return (
    <div style={{ flex: 1, padding: '20px', overflowY: 'auto', background: '#121212' }}>
      <h3 style={{ margin: '0 0 15px 0', color: '#fff' }}>📺 Витрина поиска</h3>
      
      {units.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#555' }}>
          {searchQuery 
            ? 'Ничего не найдено по данному серийному номеру' 
            : 'Используйте верхнюю строку поиска для сканирования деталей'}
        </div>
      ) : (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', 
          gap: '15px' 
        }}>
          {units.map(unit => (
            <div 
              key={unit.id} 
              style={{ 
                background: '#1a1a1a', 
                border: '1px solid #333', 
                borderRadius: '6px', 
                padding: '15px', 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '10px' 
              }}
            >
              <div>
                <span style={{ 
                  fontSize: '11px', 
                  background: unit.physical_status === 'IN_STORE' ? '#2ea44f' : '#ff4d4d', 
                  color: '#fff', 
                  padding: '2px 6px', 
                  borderRadius: '3px', 
                  fontWeight: 'bold' 
                }}>
                  {unit.physical_status}
                </span>
                <div style={{ fontSize: '12px', color: '#888', marginTop: '6px' }}>
                  SN: {unit.unique_serial_number}
                </div>
                <h4 style={{ margin: '4px 0 0 0', color: '#fff' }}>{unit.name}</h4>
              </div>
              
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                marginTop: 'auto' 
              }}>
                <span style={{ fontWeight: 'bold', color: '#4fa8ff' }}>
                  {unit.recommended_retail_price.toFixed(2)} ₽
                </span>
                <button 
                  onClick={() => onAddToBag(unit)}
                  style={{ 
                    background: '#2ea44f', 
                    color: '#fff', 
                    border: 'none', 
                    padding: '6px 12px', 
                    borderRadius: '4px', 
                    cursor: 'pointer', 
                    fontWeight: 'bold' 
                  }}
                >
                  Добавить в чек
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
