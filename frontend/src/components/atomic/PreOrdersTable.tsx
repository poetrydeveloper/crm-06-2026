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
  onExcludeProduct: (productId: number) => void; // 🔥 Новый пропс для галочки исключения
}

export const PreOrdersTable: React.FC<PreOrdersTableProps> = ({ records, onQuickOrder, onExcludeProduct }) => {
  return (
    <div style={{ background: '#1a1a1a', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>
      <h3 style={{ margin: '0 0 15px 0', color: '#ffb74d' }}>🚨 Рекомендации по ликвидации дефицита (Сгенерировано Rule Engine)</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px', textAlign: 'left' }}>
        <thead>
          <tr style={{ background: '#222', color: '#aaa', borderBottom: '2px solid #333' }}>
            <th style={{ padding: '10px' }}>Код</th>
            <th style={{ padding: '10px' }}>Товар</th>
            <th style={{ padding: '10px' }}>Причина срабатывания тега</th>
            <th style={{ padding: '10px' }}>Реком. закупка</th>
            <th style={{ padding: '10px' }}>Цена единицы</th>
            <th style={{ padding: '10px', textAlign: 'right' }}>Действия снабжения</th>
          </tr>
        </thead>
        <tbody>
          {records.length === 0 ? (
            <tr>
              <td colSpan={6} style={{ padding: '20px', textAlign: 'center', color: '#555' }}>
                📭 На полках нет дефицита по вашим правилам или все товары в исключениях.
              </td>
            </tr>
          ) : (
            records.map(r => (
              <tr key={r.pre_order_id} style={{ borderBottom: '1px solid #2d2d2d' }}>
                <td style={{ padding: '10px', color: '#888', fontFamily: 'monospace' }}>{r.product_code}</td>
                <td style={{ padding: '10px', fontWeight: 'bold' }}>{r.product_name}</td>
                <td style={{ padding: '10px', color: '#ffb74d' }}>{r.risk_level}</td>
                <td style={{ padding: '10px', fontWeight: 'bold' }}>{r.recommended_qty} шт.</td>
                <td style={{ padding: '10px', color: '#2ea44f' }}>{r.estimated_purchase_price.toFixed(2)} ₽</td>
                <td style={{ padding: '10px', textAlign: 'right', display: 'flex', gap: '8px', justifyContent: 'flex-end', alignItems: 'center' }}>
                  
                  {/* 🔥 ИНТЕЛЛЕКТУАЛЬНАЯ ГАЛОЧКА: Больше не находить этот товар в автозаказах */}
                  <button
                    onClick={() => {
                      if (confirm(`Забанить товар "${r.product_name}" в предзаказах? Система больше не будет выводить его в рекомендации.`)) {
                        onExcludeProduct(r.product_id);
                      }
                    }}
                    style={{ background: '#333', color: '#ff4d4d', border: '1px solid #444', padding: '6px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}
                    title="Поместить в список исключений (Больше не находить)"
                  >
                    🚫 Больше не находить
                  </button>

                  <button
                    onClick={() => onQuickOrder(r)}
                    style={{ background: '#4fa8ff', color: '#000', border: 'none', padding: '6px 14px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                  >
                    Оформить заказ
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};
