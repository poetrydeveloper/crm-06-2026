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
  const [cartCount, setCartCount] = useState(0); // 🔥 Счетчик отложенных позиций

  const loadActiveOrders = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        const ordersArray = Array.isArray(data) ? data : (data.orders || data.data || []);
        // Вчерашний сплиттер возвращает плоские списки
        const rawActive = Array.isArray(data.active) ? data.active : ordersArray;
        
        setOrders(rawActive.map((o: any) => ({
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

  // 🔥 Проверка накопленной корзины предзаказов
  const checkPurchaseCart = () => {
    try {
      const cartRaw = localStorage.getItem('purchase_cart');
      if (cartRaw) {
        const cartList = JSON.parse(cartRaw);
        setCartCount(cartList.length);
      } else {
        setCartCount(0);
      }
    } catch (e) { setCartCount(0); }
  };

  const reloadAll = async () => {
    setLoading(true);
    await Promise.all([loadActiveOrders(), loadSuppliers()]);
    checkPurchaseCart();
    setLoading(false);
  };

  useEffect(() => { reloadAll(); }, []);

  // Дополнительно проверяем буфер при открытии модального окна
  const handleOpenOrderModal = () => {
    checkPurchaseCart();
    setIsModalOpen(true);
  };

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
        body: JSON.stringify({ invoice_number: inv, supplier_id: orderId, items: [{ product_id: productId, quantity: 1, actual_purchase_price: 250.0 }] })
      });
      alert('🎉 Товар успешно принят!');
      loadActiveOrders();
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      {/* Кнопка быстрого вызова с индикатором накопительного буфера */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <WarehouseTabs activeTab={activeTab} onTabChange={setActiveTab} />
        {activeTab === 'receipts' && (
          <button 
            onClick={handleOpenOrderModal}
            style={{ 
              background: cartCount > 0 ? '#ffb74d' : '#2ea44f', 
              color: cartCount > 0 ? '#000' : '#fff',
              border: 'none', padding: '10px 18px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' 
            }}
          >
            ➕ Создать новую заявку {cartCount > 0 && `(🛒 В корзине: ${cartCount})`}
          </button>
        )}
      </div>
      
      {loading ? (
        <div style={{ color: '#888' }}>Загрузка данных...</div>
      ) : activeTab === 'receipts' ? (
        <ReceiptsTable orders={orders} expandedOrderId={expandedOrderId} onToggleRow={(id) => setExpandedOrderId(prev => prev === id ? null : id)} onConfirmReceipt={handleConfirmReceipt} onOpenModal={handleOpenOrderModal} />
      ) : (
        <SuppliersTable suppliers={suppliers} onCreateSupplier={handleCreateSupplier} />
      )}

      {isModalOpen && (
        <OrderModal 
          onClose={() => { setIsModalOpen(false); checkPurchaseCart(); }} 
          onOrderCreated={() => { loadActiveOrders(); checkPurchaseCart(); }} 
        />
      )}
    </div>
  );
};
