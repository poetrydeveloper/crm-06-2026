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
  onOpenModal,
}) => {
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, color: '#fff' }}>📋 Накладные в пути (IN_DELIVERY)</h3>
        <button 
          onClick={onOpenModal} 
          style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          + Создать новую заявку
        </button>
      </div>

      {orders.length === 0 ? (
        <div style={{ padding: '30px', background: '#1a1a1a', borderRadius: '8px', border: '1px solid #333', textAlign: 'center', color: '#666' }}>
          📭 На данный момент нет активных незакрытых заявок поставщикам.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
            <thead>
              <tr style={{ background: '#222', borderBottom: '2px solid #333', textAlign: 'left' }}>
                <th style={{ padding: '12px', width: '40px' }}></th>
                <th style={{ padding: '12px' }}>ID Заявки</th>
                <th style={{ padding: '12px' }}>Поставщик</th>
                <th style={{ padding: '12px' }}>Фин. Нагрузка</th>
                <th style={{ padding: '12px' }}>Статус</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(order => (
                <React.Fragment key={order.supplier_order_id}>
                  <tr 
                    onClick={() => onToggleRow(order.supplier_order_id)}
                    style={{ borderBottom: '1px solid #333', cursor: 'pointer', background: expandedOrderId === order.supplier_order_id ? '#252525' : 'transparent' }}
                  >
                    <td style={{ padding: '12px', textAlign: 'center', color: '#888' }}>
                      {expandedOrderId === order.supplier_order_id ? '▼' : '►'}
                    </td>
                    <td style={{ padding: '12px', fontWeight: 'bold' }}>#{order.supplier_order_id}</td>
                    <td style={{ padding: '12px' }}>{order.supplier_name}</td>
                    <td style={{ padding: '12px', color: '#2ea44f' }}>{order.total_financial_load.toFixed(2)} ₽</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ 
                        background: order.status === 'Выставлено на полку' ? '#1b5e20' : '#2d2d2d', 
                        padding: '3px 8px', borderRadius: '4px', fontSize: '12px', 
                        color: order.status === 'Выставлено на полку' ? '#a5d6a7' : '#ffb74d' 
                      }}>{order.status}</span>
                    </td>
                  </tr>

                  {expandedOrderId === order.supplier_order_id && (
                    <tr>
                      <td colSpan={5} style={{ background: '#1e1e1e', padding: '15px', borderBottom: '1px solid #333' }}>
                        <div style={{ borderLeft: '3px solid #4fa8ff', paddingLeft: '15px' }}>
                          <h4 style={{ margin: '0 0 10px 0', color: '#4fa8ff' }}>📋 Состав позиций в заказе:</h4>
                          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#121212', fontSize: '14px' }}>
                            <thead>
                              <tr style={{ background: '#1a1a1a', color: '#aaa', textAlign: 'left', borderBottom: '1px solid #333' }}>
                                <th style={{ padding: '8px' }}>Код/Артикул</th>
                                <th style={{ padding: '8px' }}>Название товара</th>
                                <th style={{ padding: '8px' }}>Ожидаемое кол-во</th>
                                <th style={{ padding: '8px' }}>Цена закупки</th>
                                <th style={{ padding: '8px', textAlign: 'right' }}>Действие</th>
                              </tr>
                            </thead>
                            <tbody>
                              {order.items?.map(item => (
                                <tr key={item.product_id} style={{ borderBottom: '1px solid #222' }}>
                                  <td style={{ padding: '8px', color: '#888' }}>{item.product_code}</td>
                                  <td style={{ padding: '8px', fontWeight: '500' }}>{item.product_name}</td>
                                  <td style={{ padding: '8px' }}>{item.quantity} шт.</td>
                                  <td style={{ padding: '8px', color: '#2ea44f' }}>{item.estimated_purchase_price.toFixed(2)} ₽</td>
                                  <td style={{ padding: '8px', textAlign: 'right' }}>
                                    {order.status !== 'Выставлено на полку' ? (
                                      <button 
                                        onClick={(e) => { e.stopPropagation(); onConfirmReceipt(order.supplier_order_id, item.product_id); }}
                                        style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '4px 8px', borderRadius: '3px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}
                                      >
                                        Принять на полку
                                      </button>
                                    ) : (
                                      <span style={{ color: '#888', fontSize: '12px' }}>✔️ Оприходован</span>
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
};
