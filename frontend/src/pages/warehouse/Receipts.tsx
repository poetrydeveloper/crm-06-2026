// frontend/src/pages/warehouse/Receipts.tsx
import React, { useState, useEffect } from 'react';

interface SupplierOrder {
  supplier_order_id: number;
  supplier_name: string;
  total_financial_load: number;
  status: string;
}

export const Receipts: React.FC = () => {
  const [orders, setOrders] = useState<SupplierOrder[]>([]);
  const [loading, setLoading] = useState(true);

  // 📥 Тянем активные заявки с бэкенда ядра через шлюз
  const loadActiveOrders = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        // Фильтруем только незакрытые (например, со статусом EXPECTED или IN_DELIVERY)
        setOrders(data.filter((o: SupplierOrder) => o.status !== 'CLOSED'));
      }
    } catch (error) {
      console.error('Ошибка загрузки заявок склада:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActiveOrders();
  }, []);

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#4fa8ff' }}>📦 Приемка накладных и Логистика</h2>
        <button onClick={loadActiveOrders} style={{ background: '#333', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>
          🔄 Обновить
        </button>
      </div>

      {loading ? (
        <div style={{ color: '#888' }}>Загрузка открытых поставок...</div>
      ) : orders.length === 0 ? (
        <div style={{ padding: '30px', background: '#1a1a1a', borderRadius: '8px', border: '1px solid #333', textAlign: 'center', color: '#666' }}>
          📭 На данный момент нет активных незакрытых заявок поставщикам.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
            <thead>
              <tr style={{ background: '#222', borderBottom: '2px solid #333', textAlign: 'left' }}>
                <th style={{ padding: '12px' }}>ID Заявки</th>
                <th style={{ padding: '12px' }}>Поставщик</th>
                <th style={{ padding: '12px' }}>Фин. Нагрузка</th>
                <th style={{ padding: '12px' }}>Статус</th>
                <th style={{ padding: '12px' }}>Действие</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(order => (
                <tr key={order.supplier_order_id} style={{ borderBottom: '1px solid #333' }}>
                  <td style={{ padding: '12px', fontWeight: 'bold' }}>#{order.supplier_order_id}</td>
                  <td style={{ padding: '12px' }}>{order.supplier_name}</td>
                  <td style={{ padding: '12px', color: '#2ea44f' }}>{order.total_financial_load.toFixed(2)} ₽</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ background: '#2d2d2d', padding: '3px 8px', borderRadius: '4px', fontSize: '12px', color: '#ffb74d' }}>
                      {order.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <button style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                      Принять накладную
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
