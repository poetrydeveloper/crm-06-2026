// frontend/src/pages/warehouse/Receipts.tsx
import React, { useState, useEffect } from 'react';
import { WarehouseTabs } from '../../components/atomic/WarehouseTabs';
import { ReceiptsTable } from '../../components/atomic/ReceiptsTable';
import { SuppliersTable } from '../../components/atomic/SuppliersTable';
import { OrderModal } from '../../components/atomic/OrderModal';

interface ProductItem {
  product_id: number;
  product_name: string;
  product_code: string;
  units: Array<{
    unit_id: number;
    unique_serial_number: string;
    purchase_price: number;
    physical_status: string;
  }>;
  expected_count: number;
  total_count: number;
}

interface SupplierOrder {
  order_key: string;
  order_date: string;
  supplier_id: number;
  supplier_name: string;
  total_financial_load: number;
  products: ProductItem[];
}

interface Supplier {
  supplier_id: number;
  name: string;
}

const DAY_OPTIONS = [
  { label: '7 дней', value: 7 },
  { label: '10 дней', value: 10 },
  { label: '30 дней', value: 30 },
  { label: 'Все', value: 365 },
];

export const Receipts: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'receipts' | 'suppliers'>('receipts');
  const [orders, setOrders] = useState<SupplierOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [expandedOrderKey, setExpandedOrderKey] = useState<string | null>(null);
  const [cartCount, setCartCount] = useState(0);
  const [days, setDays] = useState(10);

  const loadSuppliersList = async () => {
    try {
      const res = await fetch('/api/v1/warehouse/suppliers');
      if (res.ok) {
        const data = await res.json();
        const arr = Array.isArray(data) ? data : data.suppliers || [];
        setSuppliers(arr);
        return arr;
      }
    } catch {}
    return [];
  };

  const loadActiveOrders = async () => {
    try {
      await loadSuppliersList();
      const res = await fetch(`/api/v1/warehouse/orders/active?days=${days}`);
      if (res.ok) {
        const data = await res.json();
        setOrders(data.orders || []);
      }
    } catch {}
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

  useEffect(() => { reloadAll(); }, [days]);

  const handleToggleRow = (key: string) => {
    setExpandedOrderKey((prev) => (prev === key ? null : key));
  };

  const handleConfirmReceipt = async (supplierId: number, unitIds: number[]) => {
    try {
      const res = await fetch('/api/v1/warehouse/receipts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ supplier_id: supplierId, unit_ids: unitIds }),
      });
      if (res.ok) {
        alert(`Принято: ${unitIds.length} шт.`);
        loadActiveOrders();
      }
    } catch {}
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

      {activeTab === 'receipts' && (
        <div className="d-flex gap-8 mb-3">
          {DAY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              className={`btn btn-sm ${days === opt.value ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setDays(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <div className="loading-text">Загрузка...</div>
      ) : activeTab === 'receipts' ? (
        <ReceiptsTable
          orders={orders}
          expandedOrderKey={expandedOrderKey}
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