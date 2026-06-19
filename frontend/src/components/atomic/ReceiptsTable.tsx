// frontend/src/components/atomic/ReceiptsTable.tsx
import React, { useState } from 'react';

interface OrderItem {
  unit_id: number;
  product_id: number;
  product_name: string;
  product_code: string;
  unique_serial_number: string;
  purchase_price: number;
  physical_status: string;
}

interface SupplierOrder {
  supplier_order_id: number;
  supplier_name: string;
  total_financial_load: number;
  status: string;
}

interface ReceiptsTableProps {
  orders: SupplierOrder[];
  expandedOrderId: number | null;
  orderItems: Record<number, OrderItem[]>;
  onToggleRow: (id: number) => void;
  onConfirmReceipt?: (supplierId: number, productId: number) => void;
  onOpenModal: () => void;
}

export const ReceiptsTable: React.FC<ReceiptsTableProps> = ({
  orders,
  expandedOrderId,
  orderItems,
  onToggleRow,
  onOpenModal,
}) => {
  const [acceptedUnits, setAcceptedUnits] = useState<Set<number>>(new Set());
  const [acceptedDates, setAcceptedDates] = useState<Record<number, string>>({});

  const handleAccept = async (supplierId: number, unitId: number) => {
    try {
      const response = await fetch('/api/v1/warehouse/receipts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_id: supplierId,
          unit_ids: [unitId],
        }),
      });

      const data = await response.json();

      if (response.ok && data.accepted_count > 0) {
        setAcceptedUnits((prev) => new Set(prev).add(unitId));
        setAcceptedDates((prev) => ({
          ...prev,
          [unitId]: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
        }));
      }

      if (data.errors && data.errors.length > 0) {
        alert(data.errors.join('\n'));
      }
    } catch (e) {
      console.error('Ошибка приёмки:', e);
      alert('Сетевая ошибка при приёмке');
    }
  };

  if (orders.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted" style={{ margin: 0 }}>
          Нет активных заявок
        </p>
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
          {orders.map((order) => {
            const items = orderItems[order.supplier_order_id] || [];
            const allAccepted = items.length > 0 && items.every((item) => acceptedUnits.has(item.unit_id));

            return (
              <React.Fragment key={order.supplier_order_id}>
                <tr
                  onClick={() => onToggleRow(order.supplier_order_id)}
                  style={{
                    cursor: 'pointer',
                    background: expandedOrderId === order.supplier_order_id ? 'var(--bg-secondary)' : undefined,
                  }}
                >
                  <td style={{ textAlign: 'center' }}>
                    {expandedOrderId === order.supplier_order_id ? '▼' : '►'}
                  </td>
                  <td style={{ fontWeight: 600 }}>#{order.supplier_order_id}</td>
                  <td>{order.supplier_name}</td>
                  <td style={{ color: 'var(--success)', fontWeight: 600 }}>
                    {order.total_financial_load.toFixed(2)} ₽
                  </td>
                  <td>
                    <span className={`badge ${allAccepted ? 'badge-success' : 'badge-warning'}`}>
                      {allAccepted ? 'Выставлено на полку' : order.status}
                    </span>
                  </td>
                </tr>

                {expandedOrderId === order.supplier_order_id && (
                  <tr>
                    <td colSpan={5} style={{ padding: '16px', background: 'var(--bg-secondary)' }}>
                      {items.length === 0 ? (
                        <div className="text-muted text-center" style={{ padding: '20px' }}>
                          Загрузка состава...
                        </div>
                      ) : (
                        <>
                          <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600 }}>
                            Состав заказа ({items.length} поз.)
                          </h4>
                          <table className="table" style={{ margin: 0 }}>
                            <thead>
                              <tr>
                                <th>Код</th>
                                <th>Товар</th>
                                <th>Серийный номер</th>
                                <th>Цена</th>
                                <th style={{ textAlign: 'right' }}>Действие</th>
                              </tr>
                            </thead>
                            <tbody>
                              {items.map((item) => (
                                <tr key={item.unit_id}>
                                  <td className="text-mono">{item.product_code}</td>
                                  <td style={{ textTransform: 'capitalize' }}>{item.product_name}</td>
                                  <td className="text-mono" style={{ fontSize: '12px' }}>
                                    {item.unique_serial_number}
                                  </td>
                                  <td style={{ color: 'var(--success)' }}>
                                    {item.purchase_price.toFixed(2)} ₽
                                  </td>
                                  <td style={{ textAlign: 'right' }}>
                                    {acceptedUnits.has(item.unit_id) ? (
                                      <span className="badge badge-success" style={{ fontSize: '12px' }}>
                                        ✔ Принят {acceptedDates[item.unit_id]}
                                      </span>
                                    ) : (
                                      <button
                                        className="btn btn-success btn-sm"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleAccept(order.supplier_order_id, item.unit_id);
                                        }}
                                      >
                                        Принять
                                      </button>
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </>
                      )}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};