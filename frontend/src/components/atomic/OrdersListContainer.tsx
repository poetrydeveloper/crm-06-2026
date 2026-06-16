// frontend/src/components/atomic/OrdersListContainer.tsx
import React from 'react';
import { TimelineCard } from './TimelineCard';

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

interface OrdersListContainerProps {
  orders: TimelineOrder[];
  emptyMessage: string;
}

export const OrdersListContainer: React.FC<OrdersListContainerProps> = ({ orders, emptyMessage }) => {
  if (orders.length === 0) {
    return (
      <div style={{ 
        padding: '40px', background: '#1a1a1a', borderRadius: '8px', 
        border: '1px solid #333', textAlign: 'center', color: '#555' 
      }}>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
      {orders.map(order => (
        <TimelineCard key={order.supplier_order_id} order={order} />
      ))}
    </div>
  );
};
