// frontend/src/pages/warehouse/Receipts.tsx
import React, { useState, useEffect } from 'react';
import { WarehouseTabs } from '../../components/atomic/WarehouseTabs';
import { ReceiptsTable } from '../../components/atomic/ReceiptsTable';
import { SuppliersTable } from '../../components/atomic/SuppliersTable';
import { OrderModal } from '../../components/atomic/OrderModal';

interface SupplierOrder {
  supplier_order_id: number;
  supplier_name: string;
  order_date: string;
  total_financial_load: number;
  status: string;
  items: Array<{
    product_id: number;
    product_name: string;
    product_code: string;
    qty_in_order: number;
    avg_purchase_price: number;
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
  const [expandedOrderId, setExpandedOrderId] = useState<string | null>(null);
  const [cartCount, setCartCount] = useState(0);

  const loadSuppliersList = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/suppliers');
      if (response.ok) {
        const data = await response.json();
        const arr = Array.isArray(data) ? data : data.suppliers || [];
        setSuppliers(arr);
        return arr;
      }
    } catch (e) {
      console.error(e);
    }
    return [];
  };

  const loadActiveOrders = async () => {
    try {
      await loadSuppliersList();

      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        const activeOrders = (data.active || []).map((o: any) => ({
          supplier_order_id: o.supplier_id,
          supplier_name: o.supplier_name,
          order_date: o.order_date,
          total_financial_load: o.items.reduce((sum: number, i: any) => sum + (i.avg_purchase_price || 0) * (i.qty_in_order || 0), 0),
          status: 'В ПУТИ',
          items: o.items || [],
        }));
        setOrders(activeOrders);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const checkPurchaseCart = () => {
    try {
      const raw = localStorage.getItem('purchase_cart');
      setCartCount(raw ? JSON.parse(raw).length : 0);
    } catch {
      setCartCount(0);
    }
  };

  const reloadAll = async () => {
    setLoading(true);
    await loadActiveOrders();
    checkPurchaseCart();
    setLoading(false);
  };

  useEffect(() => {
    reloadAll();
  }, []);

  const handleToggleRow = (id: string) => {
    setExpandedOrderId((prev) => (prev === id ? null : id));
  };

  const handleConfirmReceipt = async (supplierId: number, unitIds: number[]) => {
    try {
      const res = await fetch('/api/v1/warehouse/receipts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_id: supplierId,
          unit_ids: unitIds,
        }),
      });

      if (res.ok) {
        alert(`Принято: ${unitIds.length} шт.`);
        loadActiveOrders();
      }
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
          onToggleRow={handleToggleRow}
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
            loadSuppliersList();
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