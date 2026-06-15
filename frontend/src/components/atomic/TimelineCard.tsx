// frontend/src/components/atomic/TimelineCard.tsx
import React from 'react';

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

interface TimelineCardProps {
  order: TimelineOrder;
}

export const TimelineCard: React.FC<TimelineCardProps> = ({ order }) => {
  // Определяем активность этапов в зависимости от статуса в СУБД
  const isRequested = true; // Заявка создана всегда, раз она есть в списке
  const isInDelivery = order.status === 'IN_DELIVERY' || order.status === 'Выставлено на полку';
  const isReceived = order.status === 'Выставлено на полку';

  const stepStyle = (isActive: boolean) => ({
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    flex: 1,
    position: 'relative' as const,
    color: isActive ? '#4fa8ff' : '#555'
  });

  const circleStyle = (isActive: boolean) => ({
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    background: isActive ? '#4fa8ff' : '#2d2d2d',
    border: isActive ? 'none' : '2px solid #444',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    color: isActive ? '#000' : '#666',
    fontSize: '12px',
    marginBottom: '8px',
    zIndex: 2
  });

  return (
    <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '8px', padding: '20px', marginBottom: '15px' }}>
      {/* Шапка карточки заказа */}
      <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2d2d2d', paddingBottom: '10px', marginBottom: '15px' }}>
        <div>
          <span style={{ color: '#888', fontSize: '13px' }}>Заказ поставщику</span>
          <h3 style={{ margin: '4px 0 0 0', color: '#fff' }}>#{order.supplier_order_id} — {order.supplier_name}</h3>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ color: '#888', fontSize: '13px' }}>Фин. нагрузка</span>
          <div style={{ color: '#2ea44f', fontWeight: 'bold', marginTop: '4px' }}>{order.total_financial_load.toFixed(2)} ₽</div>
        </div>
      </div>

      {/* Список товаров внутри заказа */}
      <div style={{ fontSize: '14px', color: '#aaa', marginBottom: '20px', background: '#121212', padding: '10px', borderRadius: '4px' }}>
        <span style={{ fontSize: '11px', color: '#666', fontWeight: 'bold', display: 'block', marginBottom: '4px' }}>СОСТАВ ПОСТАВКИ:</span>
        {order.items?.map((item, idx) => (
          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>• {item.product_name}</span>
            <span style={{ color: '#fff' }}>{item.quantity} шт.</span>
          </div>
        )) || <div style={{ color: '#555' }}>Состав не указан</div>}
      </div>

      {/* Линейный интерактивный Таймлайн */}
      <div style={{ display: 'flex', position: 'relative', marginTop: '10px' }}>
        {/* Соединительная фоновая линия */}
        <div style={{ position: 'absolute', top: '11px', left: '15%', right: '15%', height: '2px', background: '#333', zIndex: 1 }} />
        
        {/* Соединительная активная линия прогресса */}
        <div style={{ 
          position: 'absolute', top: '11px', left: '15%', 
          width: isReceived ? '70%' : isInDelivery ? '35%' : '0%', 
          height: '2px', background: '#4fa8ff', zIndex: 1,
          transition: 'width 0.3s ease'
        }} />

        {/* Этап 1: Заявка */}
        <div style={stepStyle(isRequested)}>
          <div style={circleStyle(isRequested)}>1</div>
          <span style={{ fontSize: '12px', fontWeight: 'bold' }}>Заявка отправлена</span>
          <span style={{ fontSize: '10px', color: '#666' }}>Статус: EXPECTED</span>
        </div>

        {/* Этап 2: Транспортировка */}
        <div style={stepStyle(isInDelivery)}>
          <div style={circleStyle(isInDelivery)}>2</div>
          <span style={{ fontSize: '12px', fontWeight: 'bold' }}>Товар в пути</span>
          <span style={{ fontSize: '10px', color: '#666' }}>Статус: IN_DELIVERY</span>
        </div>

        {/* Этап 3: Полка */}
        <div style={stepStyle(isReceived)}>
          <div style={circleStyle(isReceived)}>3</div>
          <span style={{ fontSize: '12px', fontWeight: 'bold' }}>Выставлено на полку</span>
          <span style={{ fontSize: '10px', color: '#666' }}>Статус: IN_STORE</span>
        </div>
      </div>
    </div>
  );
};
