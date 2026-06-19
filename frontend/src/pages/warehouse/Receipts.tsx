// frontend/src/pages/warehouse/Receipts.tsx
import React, { useState, useEffect } from 'react';
import { WarehouseTabs } from '../../components/atomic/WarehouseTabs';
import { ReceiptsTable } from '../../components/atomic/ReceiptsTable';
import { SuppliersTable } from '../../components/atomic/SuppliersTable';
import { OrderModal } from '../../components/atomic/OrderModal';

interface SupplierOrder {
  supplier_order_id: number;
  supplier_name: string;
  total_financial_load: number;
  status: string;
  items?: Array<{
    product_id: number;
    product_name: string;
    product_code: string;
    quantity: number;
    estimated_purchase_price: number;
  }>;
}

interface Supplier {
  supplier_id: number;
  name: string;
}

export const Receipts: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'receipts' | 'suppliers'>('receipts');
  const [orders, setOrders] = useState<SupplierOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null);
  const [cartCount, setCartCount] = useState(0);

  const loadActiveOrders = async () => {
  try {
    // Загружаем поставщиков чтобы получить имена
    const suppResponse = await fetch('/api/v1/warehouse/suppliers');
    const suppData = suppResponse.ok ? await suppResponse.json() : [];
    const suppliersList: Supplier[] = Array.isArray(suppData) ? suppData : suppData.suppliers || [];
    const supplierNames: Record<number, string> = {};
    suppliersList.forEach((s: Supplier) => {
      supplierNames[s.supplier_id] = s.name;
    });

    const response = await fetch('/api/v1/warehouse/orders');
    if (response.ok) {
      const data = await response.json();
      const ordersArray = data.orders || [];
      setOrders(
        ordersArray.map((o: any) => ({
          supplier_order_id: o.supplier_id,
          supplier_name: supplierNames[o.supplier_id] || `Поставщик #${o.supplier_id}`,
          total_financial_load: o.total_amount || 0,
          status: 'В ПУТИ',
          items: [],
        }))
      );
    }
  } catch (e) {
    console.error(e);
  }
};

  const loadSuppliers = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/suppliers');
      if (response.ok) {
        const data = await response.json();
        const suppliersArray = Array.isArray(data) ? data : data.suppliers || [];
        setSuppliers(suppliersArray);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const checkPurchaseCart = () => {
    try {
      const cartRaw = localStorage.getItem('purchase_cart');
      setCartCount(cartRaw ? JSON.parse(cartRaw).length : 0);
    } catch {
      setCartCount(0);
    }
  };

  const reloadAll = async () => {
    setLoading(true);
    await Promise.all([loadActiveOrders(), loadSuppliers()]);
    checkPurchaseCart();
    setLoading(false);
  };

  useEffect(() => {
    reloadAll();
  }, []);

  const handleConfirmReceipt = async (orderId: number, productId: number) => {
    const inv = prompt('Номер накладной:', `INV-${Date.now().toString().slice(-6)}`);
    if (!inv) return;
    try {
      await fetch('/api/v1/warehouse/receipts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_id: orderId,
          items: [{ product_id: productId, quantity: 1, actual_purchase_price: 250.0 }],
        }),
      });
      alert('Товар принят на полку');
      loadActiveOrders();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="page-content">
      <div className="d-flex justify-between align-center mb-3">
        <WarehouseTabs activeTab={activeTab} onTabChange={setActiveTab} />
        {activeTab === 'receipts' && (
          <button
            className={cartCount > 0 ? 'btn btn-warning' : 'btn btn-success'}
            onClick={() => { checkPurchaseCart(); setIsModalOpen(true); }}
          >
            Новая заявка {cartCount > 0 && `(🛒 ${cartCount})`}
          </button>
        )}
      </div>

      {loading ? (
        <div className="loading-text">Загрузка...</div>
      ) : activeTab === 'receipts' ? (
        <ReceiptsTable
          orders={orders}
          expandedOrderId={expandedOrderId}
          onToggleRow={(id) => setExpandedOrderId((prev) => (prev === id ? null : id))}
          onConfirmReceipt={handleConfirmReceipt}
          onOpenModal={() => setIsModalOpen(true)}
        />
      ) : (
        <SuppliersTable
          suppliers={suppliers}
          onCreateSupplier={async () => {
            const name = prompt('Название поставщика:');
            if (!name) return;
            await fetch('/api/v1/warehouse/suppliers', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name }),
            });
            loadSuppliers();
          }}
        />
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