// frontend/src/components/atomic/OrderModalItemsTable.tsx
import React from 'react';

export interface PurchaseItem {
  product_id: number;
  product_name?: string;
  product_code?: string;
  quantity: number;
  estimated_purchase_price: number;
}

interface OrderModalItemsTableProps {
  items: PurchaseItem[];
  onItemChange: (index: number, field: keyof PurchaseItem, value: any) => void;
  onRemoveItem: (index: number) => void;
}

export const OrderModalItemsTable: React.FC<OrderModalItemsTableProps> = ({
  items,
  onItemChange,
  onRemoveItem
}) => {
  if (items.length === 0) {
    return (
      <div style={{ padding: '15px', background: '#121212', borderRadius: '4px', textAlign: 'center', color: '#666', fontSize: '13px' }}>
        🛒 Список позиций пуст. Добавьте вручную или накопите через Умный Предзаказ.
      </div>
    );
  }

  return (
    <div style={{ maxHeight: '180px', overflowY: 'auto', background: '#121212', borderRadius: '4px', border: '1px solid #333' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
        <thead>
          <tr style={{ background: '#222', color: '#aaa', borderBottom: '1px solid #333' }}>
            <th style={{ padding: '8px' }}>ID/Товар</th>
            <th style={{ padding: '8px', width: '70px' }}>Кол-во</th>
            <th style={{ padding: '8px', width: '90px' }}>Цена (₽)</th>
            <th style={{ padding: '8px', width: '40px', textAlign: 'right' }}>Удал.</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid #2d2d2d' }}>
              <td style={{ padding: '8px' }}>
                <div style={{ fontWeight: 'bold', color: '#4fa8ff' }}>#{item.product_id}</div>
                <div style={{ fontSize: '11px', color: '#888', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '160px' }}>
                  {item.product_name || 'Ручной ввод'}
                </div>
              </td>
              <td style={{ padding: '8px' }}>
                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => onItemChange(idx, 'quantity', parseInt(e.target.value) || 1)}
                  style={{ width: '100%', padding: '4px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '3px', textAlign: 'center' }}
                />
              </td>
              <td style={{ padding: '8px' }}>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={item.estimated_purchase_price}
                  onChange={(e) => onItemChange(idx, 'estimated_purchase_price', parseFloat(e.target.value) || 0)}
                  style={{ width: '100%', padding: '4px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '3px', textAlign: 'right' }}
                />
              </td>
              <td style={{ padding: '8px', textAlign: 'right' }}>
                <button
                  type="button"
                  onClick={() => onRemoveItem(idx)}
                  style={{ background: 'transparent', color: '#ff4d4d', border: 'none', cursor: 'pointer', fontSize: '14px' }}
                >
                  ❌
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
