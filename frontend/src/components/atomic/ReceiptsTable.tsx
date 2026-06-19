// frontend/src/components/atomic/ReceiptsTable.tsx
import React from 'react';

interface OrderItem {
  product_id: number;
  product_name: string;
  product_code: string;
  quantity: number;
  estimated_purchase_price: number;
}

interface SupplierOrder {
  supplier_order_id: number;
  supplier_name: string;
  total_financial_load: number;
  status: string;
  items?: OrderItem[];
}

interface ReceiptsTableProps {
  orders: SupplierOrder[];
  expandedOrderId: number | null;
  onToggleRow: (id: number) => void;
  onConfirmReceipt: (orderId: number, productId: number) => void;
  onOpenModal: () => void;
}

export const ReceiptsTable: React.FC<ReceiptsTableProps> = ({
  orders,
  expandedOrderId,
  onToggleRow,
  onConfirmReceipt,
}) => {
  if (orders.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted" style={{ margin: 0 }}>Нет активных заявок</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            <th style={{ width: '40px' }}></th>
            <th>ID заявки</th>
            <th>Поставщик</th>
            <th>Сумма</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <React.Fragment key={order.supplier_order_id}>
              <tr
                onClick={() => onToggleRow(order.supplier_order_id)}
                style={{ cursor: 'pointer', background: expandedOrderId === order.supplier_order_id ? 'var(--bg-secondary)' : undefined }}
              >
                <td style={{ textAlign: 'center' }}>{expandedOrderId === order.supplier_order_id ? '▼' : '►'}</td>
                <td style={{ fontWeight: 600 }}>#{order.supplier_order_id}</td>
                <td>{order.supplier_name}</td>
                <td style={{ color: 'var(--success)', fontWeight: 600 }}>{order.total_financial_load.toFixed(2)} ₽</td>
                <td>
                  <span className={`badge ${order.status === 'Выставлено на полку' ? 'badge-success' : 'badge-warning'}`}>
                    {order.status}
                  </span>
                </td>
              </tr>

              {expandedOrderId === order.supplier_order_id && order.items && (
                <tr>
                  <td colSpan={5} style={{ padding: '16px', background: 'var(--bg-secondary)' }}>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600 }}>Состав заказа:</h4>
                    <table className="table" style={{ margin: 0 }}>
                      <thead>
                        <tr>
                          <th>Код</th>
                          <th>Товар</th>
                          <th>Кол-во</th>
                          <th>Цена</th>
                          <th style={{ textAlign: 'right' }}>Действие</th>
                        </tr>
                      </thead>
                      <tbody>
                        {order.items.map((item) => (
                          <tr key={item.product_id}>
                            <td className="text-mono">{item.product_code}</td>
                            <td>{item.product_name}</td>
                            <td>{item.quantity} шт.</td>
                            <td style={{ color: 'var(--success)' }}>{item.estimated_purchase_price.toFixed(2)} ₽</td>
                            <td style={{ textAlign: 'right' }}>
                              {order.status !== 'Выставлено на полку' ? (
                                <button
                                  className="btn btn-success btn-sm"
                                  onClick={(e) => { e.stopPropagation(); onConfirmReceipt(order.supplier_order_id, item.product_id); }}
                                >
                                  Принять
                                </button>
                              ) : (
                                <span className="text-muted" style={{ fontSize: '12px' }}>✔ Оприходован</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
};