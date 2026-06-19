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
  onExcludeProduct: (productId: number) => void;
}

export const PreOrdersTable: React.FC<PreOrdersTableProps> = ({ records, onQuickOrder, onExcludeProduct }) => {
  return (
    <div className="card">
      <h3 className="card-title">Рекомендации по дефициту</h3>
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Код</th>
              <th>Товар</th>
              <th>Причина</th>
              <th>Кол-во</th>
              <th>Цена</th>
              <th style={{ textAlign: 'right' }}>Действия</th>
            </tr>
          </thead>
          <tbody>
            {records.length === 0 ? (
              <tr>
                <td colSpan={6} className="empty-row">Нет рекомендаций</td>
              </tr>
            ) : (
              records.map((r) => (
                <tr key={r.pre_order_id}>
                  <td className="text-mono">{r.product_code}</td>
                  <td style={{ fontWeight: 500 }}>{r.product_name}</td>
                  <td className="text-muted">{r.risk_level}</td>
                  <td style={{ fontWeight: 600 }}>{r.recommended_qty} шт.</td>
                  <td style={{ color: 'var(--success)', fontWeight: 600 }}>{r.estimated_purchase_price.toFixed(2)} ₽</td>
                  <td>
                    <div className="d-flex gap-8" style={{ justifyContent: 'flex-end' }}>
                      <button className="btn btn-sm btn-danger" onClick={() => onExcludeProduct(r.product_id)}>
                        Исключить
                      </button>
                      <button className="btn btn-sm btn-primary" onClick={() => onQuickOrder(r)}>
                        В заказ
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};