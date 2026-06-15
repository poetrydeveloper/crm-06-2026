// frontend/src/components/atomic/PreOrdersTable.tsx
import React from 'react';

export interface PreOrderRecord {
  pre_order_id: number;
  product_id: number;
  product_name: string;
  product_code: string;
  risk_level: string;
  recommended_qty: number;
  estimated_purchase_price: number;
}

interface PreOrdersTableProps {
  records: PreOrderRecord[];
  onQuickOrder: (record: PreOrderRecord) => void;
}

export const PreOrdersTable: React.FC<PreOrdersTableProps> = ({ records, onQuickOrder }) => {
  return (
    <div style={{ background: '#1a1a1a', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>
      <h3 style={{ margin: '0 0 15px 0', color: '#ffb74d' }}>🚨 Рекомендации по ликвидации дефицита</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px', textAlign: 'left' }}>
        <thead>
          <tr style={{ background: '#222', color: '#aaa', borderBottom: '2px solid #333' }}>
            <th style={{ padding: '10px' }}>Код</th>
            <th style={{ padding: '10px' }}>Товар</th>
            <th style={{ padding: '10px' }}>Уровень Риска</th>
            <th style={{ padding: '10px' }}>Реком. Кол-во</th>
            <th style={{ padding: '10px' }}>Цена закупки</th>
            <th style={{ padding: '10px', textAlign: 'right' }}>Действие</th>
          </tr>
        </thead>
        <tbody>
          {records.map(r => (
            <tr key={r.pre_order_id} style={{ borderBottom: '1px solid #2d2d2d' }}>
              <td style={{ padding: '10px', color: '#888' }}>{r.product_code}</td>
              <td style={{ padding: '10px', fontWeight: 'bold' }}>{r.product_name}</td>
              <td style={{ padding: '10px' }}>
                <span style={{ 
                  color: r.risk_level.includes('ВЫСОКИЙ') || r.risk_level.includes('КРИТИЧЕСКИЙ') ? '#ff4d4d' : '#ffb74d',
                  fontWeight: 'bold'
                }}>
                  ⚠️ {r.risk_level}
                </span>
              </td>
              <td style={{ padding: '10px' }}>{r.recommended_qty} шт.</td>
              <td style={{ padding: '10px', color: '#2ea44f' }}>{r.estimated_purchase_price.toFixed(2)} ₽</td>
              <td style={{ padding: '10px', textAlign: 'right' }}>
                <button
                  onClick={() => onQuickOrder(r)}
                  style={{ background: '#4fa8ff', color: '#000', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                  Оформить заказ
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
