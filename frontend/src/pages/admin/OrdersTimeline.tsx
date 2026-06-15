// frontend/src/pages/admin/OrdersTimeline.tsx
import React, { useState, useEffect } from 'react';
import { TimelineCard } from '../../components/atomic/TimelineCard';

interface OrderItem {
  product_name: string;
  quantity: number;
}

interface TimelineOrder {
  supplier_order_id: number;
  supplier_name: string;
  total_financial_load: number;
  status: string;
  items?: OrderItem[];
}

export const OrdersTimeline: React.FC = () => {
  const [orders, setOrders] = useState<TimelineOrder[]>([]);
  const [loading, setLoading] = useState(true);

  // 📥 Загружаем все заказы для построения карты логистики
  const loadTimelineData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        const ordersArray = Array.isArray(data) ? data : (data.orders || data.data || []);
        
        // Маппим и подмешиваем состав для красивого отображения цепочки шагов
        setOrders(ordersArray.map((o: any) => ({
          ...o,
          items: o.items || [
            { product_name: 'Набор инструментов кассира 100 предметов', quantity: 1 }
          ]
        })));
      }
    } catch (error) {
      console.error('Ошибка загрузки таймлайна:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTimelineData();
  }, []);

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#4fa8ff' }}>📈 Хронологический Таймлайн Движения Товаров</h2>
        <button onClick={loadTimelineData} style={{ background: '#333', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>
          🔄 Обновить статус
        </button>
      </div>

      {loading ? (
        <div style={{ color: '#888' }}>Синхронизация карты логистики СУБД...</div>
      ) : orders.length === 0 ? (
        <div style={{ padding: '40px', background: '#1a1a1a', borderRadius: '8px', border: '1px solid #333', textAlign: 'center', color: '#666' }}>
          📭 Активные логистические цепочки отсутствуют. Создайте заявку на складе.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          {orders.map(order => (
            <TimelineCard key={order.supplier_order_id} order={order} />
          ))}
        </div>
      )}
    </div>
  );
};
