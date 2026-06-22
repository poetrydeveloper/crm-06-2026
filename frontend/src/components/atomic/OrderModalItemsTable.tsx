// frontend/src/components/atomic/OrderModalItemsTable.tsx
import React, { useState } from 'react';

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

export const OrderModalItemsTable: React.FC<OrderModalItemsTableProps> = ({ items, onItemChange, onRemoveItem }) => {
  const [rawPrices, setRawPrices] = useState<Record<number, string>>({});

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
            <th style={{ width: '170px' }}>Цена</th>
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
                <div className="d-flex align-center gap-4">
                  <input
                    type="text"
                    inputMode="decimal"
                    className="form-control"
                    value={rawPrices[idx] !== undefined ? rawPrices[idx] : String(item.estimated_purchase_price)}
                    onFocus={(e) => e.target.select()}
                    onChange={(e) => {
                      const raw = e.target.value.replace(',', '.');
                      setRawPrices((prev) => ({ ...prev, [idx]: raw }));
                      const val = parseFloat(raw);
                      if (!isNaN(val)) {
                        onItemChange(idx, 'estimated_purchase_price', val);
                      }
                    }}
                    style={{ width: '90px', textAlign: 'right', padding: '4px' }}
                  />
                  <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--success)', width: '65px', textAlign: 'right' }}>
                    {item.estimated_purchase_price.toFixed(2)}
                  </span>
                </div>
              </td>
              <td style={{ textAlign: 'center' }}>
                <button
                  type="button"
                  className="btn btn-sm btn-outline"
                  onClick={() => onRemoveItem(idx)}
                  style={{ border: 'none', color: 'var(--danger)' }}
                >
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