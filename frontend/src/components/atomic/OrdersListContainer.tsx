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
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="d-flex flex-column gap-16">
      {orders.map((order) => (
        <TimelineCard key={order.supplier_order_id} order={order} />
      ))}
    </div>
  );
};