// frontend/src/pages/admin/OrdersTimeline.tsx
import React, { useState, useEffect } from 'react';

type TabType = 'active' | 'archived' | 'preorder';

interface OrderItem {
  product_id: number;
  product_name: string;
  product_code: string;
  qty_in_order: number;
  avg_purchase_price: number;
  qty_in_all_orders: number;
  qty_in_store: number;
}

interface OrderGroup {
  order_key: string;
  order_date: string;
  supplier_id: number;
  supplier_name: string;
  items: OrderItem[];
}

export const OrdersTimeline: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('active');
  const [activeOrders, setActiveOrders] = useState<OrderGroup[]>([]);
  const [archivedOrders, setArchivedOrders] = useState<OrderGroup[]>([]);
  const [loading, setLoading] = useState(true);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        setActiveOrders(data.active || []);
        setArchivedOrders(data.archived || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  return (
    <div className="page-content">
      <div className="page-header">
        <div>
          <h2 className="page-title">Управление закупками</h2>
          <p className="text-muted" style={{ marginTop: '4px' }}>
            Заявки по датам и поставщикам
          </p>
        </div>
        <button className="btn btn-outline" onClick={loadOrders}>
          Обновить
        </button>
      </div>

      <div className="d-flex gap-8 mb-3">
        <button
          className={`btn btn-sm ${activeTab === 'active' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('active')}
        >
          Активные заявки
        </button>
        <button
          className={`btn btn-sm ${activeTab === 'archived' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('archived')}
        >
          Архив
        </button>
        <button
          className={`btn btn-sm ${activeTab === 'preorder' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('preorder')}
        >
          Умный предзаказ
        </button>
      </div>

      {loading ? (
        <div className="loading-text">Загрузка...</div>
      ) : (
        <>
          {activeTab === 'active' && (
            <OrdersListView orders={activeOrders} emptyMessage="Нет активных заявок" />
          )}
          {activeTab === 'archived' && (
            <OrdersListView orders={archivedOrders} emptyMessage="Архив пуст" />
          )}
          {activeTab === 'preorder' && (
            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
              <p className="text-muted">В разработке</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};


const OrdersListView: React.FC<{ orders: OrderGroup[]; emptyMessage: string }> = ({
  orders,
  emptyMessage,
}) => {
  if (orders.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div>
      {orders.map((order) => (
        <div key={order.order_key} className="card mb-3">
          <div
            className="d-flex justify-between align-center mb-3"
            style={{ borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}
          >
            <div>
              <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 600 }}>
                {order.supplier_name}
              </h3>
              <div className="text-muted" style={{ fontSize: '13px', marginTop: '2px' }}>
                {new Date(order.order_date).toLocaleDateString('ru-RU')}
              </div>
            </div>
            <span className="badge badge-info">
              {order.items.length} поз.
            </span>
          </div>

          <div className="table-wrapper">
            <table className="table" style={{ fontSize: '13px' }}>
              <thead>
                <tr>
                  <th>Артикул</th>
                  <th>Наименование</th>
                  <th style={{ textAlign: 'right' }}>Цена закупки</th>
                  <th style={{ textAlign: 'center' }}>В заявке</th>
                  <th style={{ textAlign: 'center' }}>Всего в заявках</th>
                  <th style={{ textAlign: 'center' }}>В магазине</th>
                </tr>
              </thead>
              <tbody>
                {order.items.map((item, idx) => (
                  <tr key={idx}>
                    <td className="text-mono">{item.product_code}</td>
                    <td style={{ textTransform: 'capitalize', fontWeight: 500 }}>
                      {item.product_name.replace(/_/g, ' ')}
                    </td>
                    <td style={{ textAlign: 'right', color: 'var(--success)', fontWeight: 600 }}>
                      {item.avg_purchase_price.toFixed(2)} ₽
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: 600 }}>
                      {item.qty_in_order}
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      {item.qty_in_all_orders}
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <span
                        className={`badge ${item.qty_in_store === 0 ? 'badge-danger' : item.qty_in_store < 3 ? 'badge-warning' : 'badge-success'}`}
                      >
                        {item.qty_in_store} шт.
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
};