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
  const isInDelivery = order.status === 'В ПУТИ';
  const isReceived = order.status === 'Выставлено на полку';

  return (
    <div className="card">
      <div className="d-flex justify-between align-center mb-3" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
        <div>
          <div className="text-muted" style={{ fontSize: '12px' }}>Заказ поставщику</div>
          <h3 style={{ margin: '4px 0 0 0', fontSize: '16px', fontWeight: 600 }}>
            #{order.supplier_order_id} — {order.supplier_name}
          </h3>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="text-muted" style={{ fontSize: '12px' }}>Сумма</div>
          <div style={{ fontWeight: 700, color: 'var(--success)', marginTop: '4px' }}>
            {order.total_financial_load.toFixed(2)} ₽
          </div>
        </div>
      </div>

      {order.items && order.items.length > 0 && (
        <div className="mb-3" style={{ background: 'var(--bg-secondary)', padding: '10px 12px', borderRadius: 'var(--radius-sm)', fontSize: '13px' }}>
          <div className="text-muted" style={{ fontSize: '11px', fontWeight: 600, marginBottom: '6px' }}>СОСТАВ:</div>
          {order.items.map((item, idx) => (
            <div key={idx} className="d-flex justify-between">
              <span>{item.product_name}</span>
              <span style={{ fontWeight: 500 }}>{item.quantity} шт.</span>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <div style={{ flex: 1, height: '4px', background: 'var(--bg-tertiary)', borderRadius: '2px', overflow: 'hidden' }}>
          <div
            style={{
              height: '100%',
              width: isReceived ? '100%' : isInDelivery ? '50%' : '25%',
              background: 'var(--primary)',
              borderRadius: '2px',
              transition: 'width 0.3s ease',
            }}
          />
        </div>
        <span className={`badge ${isReceived ? 'badge-success' : 'badge-warning'}`}>
          {order.status}
        </span>
      </div>
    </div>
  );
};