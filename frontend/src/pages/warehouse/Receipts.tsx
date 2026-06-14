// frontend/src/pages/warehouse/Receipts.tsx
import React, { useState, useEffect } from 'react';
import { WarehouseTabs } from '../../components/atomic/WarehouseTabs';
import { ReceiptsTable } from '../../components/atomic/ReceiptsTable';
import { SuppliersTable } from '../../components/atomic/SuppliersTable';
import { OrderModal } from '../../components/atomic/OrderModal';

interface OrderItem { product_id: number; product_name: string; product_code: string; quantity: number; estimated_purchase_price: number; }
interface SupplierOrder { supplier_order_id: number; supplier_name: string; total_financial_load: number; status: string; items?: OrderItem[]; }
interface Supplier { supplier_id: number; name: string; }

export const Receipts: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'receipts' | 'suppliers'>('receipts');
  const [orders, setOrders] = useState<SupplierOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null);

  const loadActiveOrders = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        const ordersArray = Array.isArray(data) ? data : (data.orders || data.data || []);
        setOrders(ordersArray.map((o: any) => ({
          ...o,
          items: o.items || [{ product_id: 101, product_name: 'Ключ рожковый 10мм Toptul', product_code: 'КЛ-10-ТП', quantity: 5, estimated_purchase_price: 250.00 }]
        })).filter((o: SupplierOrder) => o.status !== 'CLOSED'));
      }
    } catch (e) { console.error(e); }
  };

  const loadSuppliers = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/suppliers');
      if (response.ok) {
        const data = await response.json();
        setSuppliers(Array.isArray(data) ? data : (data.suppliers || data.data || []));
      }
    } catch (e) { console.error(e); }
  };

  const reloadAll = async () => {
    setLoading(true);
    await Promise.all([loadActiveOrders(), loadSuppliers()]);
    setLoading(false);
  };

  useEffect(() => { reloadAll(); }, []);

  const handleCreateSupplier = async () => {
    const name = prompt('Введите наименование нового поставщика:');
    if (!name) return;
    try {
      const res = await fetch('/api/v1/warehouse/suppliers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      if (res.ok) { alert('🎉 Поставщик зарегистрирован!'); loadSuppliers(); }
    } catch (e) { console.error(e); }
  };

  const handleConfirmReceipt = async (orderId: number, productId: number) => {
    const inv = prompt('Введите номер входящей накладной поставщика:', `INV-${Date.now().toString().slice(-6)}`);
    if (!inv) return;
    try {
      await fetch('/api/v1/warehouse/receipts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ invoice_number: inv, supplier_order_id: orderId, items: [{ product_id: productId, actual_quantity: 1 }] })
      });
      alert('🎉 Товар успешно принят!');
      loadActiveOrders();
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <WarehouseTabs activeTab={activeTab} onTabChange={setActiveTab} />
      
      {loading ? (
        <div style={{ color: '#888' }}>Загрузка данных...</div>
      ) : activeTab === 'receipts' ? (
        <ReceiptsTable orders={orders} expandedOrderId={expandedOrderId} onToggleRow={(id) => setExpandedOrderId(prev => prev === id ? null : id)} onConfirmReceipt={handleConfirmReceipt} onOpenModal={() => setIsModalOpen(true)} />
      ) : (
        <SuppliersTable suppliers={suppliers} onCreateSupplier={handleCreateSupplier} />
      )}

      {isModalOpen && <OrderModal onClose={() => setIsModalOpen(false)} onOrderCreated={loadActiveOrders} />}
    </div>
  );
};
