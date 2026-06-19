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
  onRemoveItem,
}) => {
  if (items.length === 0) {
    return (
      <div className="text-muted text-center" style={{ padding: '20px', fontSize: '13px' }}>
        Список позиций пуст
      </div>
    );
  }

  return (
    <div className="table-wrapper" style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: '12px' }}>
      <table className="table" style={{ fontSize: '13px' }}>
        <thead>
          <tr>
            <th>Товар</th>
            <th style={{ width: '70px' }}>Кол-во</th>
            <th style={{ width: '90px' }}>Цена</th>
            <th style={{ width: '40px' }}></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => (
            <tr key={idx}>
              <td>
                <div style={{ fontWeight: 600 }}>#{item.product_id}</div>
                <div className="text-muted" style={{ fontSize: '11px' }}>{item.product_name || '—'}</div>
              </td>
              <td>
                <input
                  type="number"
                  min="1"
                  className="form-control"
                  value={item.quantity}
                  onChange={(e) => onItemChange(idx, 'quantity', parseInt(e.target.value) || 1)}
                  style={{ padding: '4px', textAlign: 'center' }}
                />
              </td>
              <td>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  className="form-control"
                  value={item.estimated_purchase_price}
                  onChange={(e) => onItemChange(idx, 'estimated_purchase_price', parseFloat(e.target.value) || 0)}
                  style={{ padding: '4px', textAlign: 'right' }}
                />
              </td>
              <td style={{ textAlign: 'center' }}>
                <button type="button" className="btn btn-sm btn-outline" onClick={() => onRemoveItem(idx)} style={{ border: 'none', color: 'var(--danger)' }}>
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};