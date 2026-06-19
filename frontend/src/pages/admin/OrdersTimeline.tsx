// frontend/src/pages/admin/OrdersTimeline.tsx
import React, { useState, useEffect } from 'react';
import { OrdersTabs } from '../../components/atomic/OrdersTabs';
import { PreOrdersTable } from '../../components/atomic/PreOrdersTable';
import type { PreOrderRecord } from '../../components/atomic/PreOrdersTable';
import { RuleCreatorBlock } from '../../components/atomic/RuleCreatorBlock';
import { ActiveRulesList } from '../../components/atomic/ActiveRulesList';
import { OrdersListContainer } from '../../components/atomic/OrdersListContainer';

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

interface RuleRecord {
  id: number;
  price_operator: string;
  price_value: number;
  name_contains: string | null;
  stock_threshold: number;
}

type TabType = 'active' | 'archived' | 'preorder';

export const OrdersTimeline: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('active');
  const [activeOrders, setActiveOrders] = useState<TimelineOrder[]>([]);
  const [archivedOrders, setArchivedOrders] = useState<TimelineOrder[]>([]);
  const [preOrders, setPreOrders] = useState<PreOrderRecord[]>([]);
  const [rules, setRules] = useState<RuleRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const loadOrdersData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        setActiveOrders(data.active || []);
        setArchivedOrders(data.archived || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadPreOrdersData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/pre-orders');
      if (response.ok) {
        const data = await response.json();
        const items = Array.isArray(data?.data) ? data.data : Array.isArray(data) ? data : [];
        setPreOrders(items);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadRulesData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/purchase-rules');
      if (response.ok) {
        const data = await response.json();
        setRules(Array.isArray(data) ? data : []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const syncAllData = async () => {
    setLoading(true);
    await Promise.all([loadOrdersData(), loadPreOrdersData(), loadRulesData()]);
    setLoading(false);
  };

  useEffect(() => {
    syncAllData();
  }, []);

  const handleQuickOrder = (record: PreOrderRecord) => {
    try {
      const cartRaw = localStorage.getItem('purchase_cart');
      const cartList = cartRaw ? JSON.parse(cartRaw) : [];
      const existingIdx = cartList.findIndex((item: any) => item.product_id === record.product_id);

      if (existingIdx > -1) {
        cartList[existingIdx].quantity += record.recommended_qty;
      } else {
        cartList.push({
          product_id: record.product_id,
          product_name: record.product_name,
          product_code: record.product_code,
          quantity: record.recommended_qty,
          estimated_purchase_price: record.estimated_purchase_price,
        });
      }

      localStorage.setItem('purchase_cart', JSON.stringify(cartList));
      alert(`Товар "${record.product_name}" добавлен в корзину`);
      setPreOrders((prev) => prev.filter((p) => p.pre_order_id !== record.pre_order_id));
    } catch (e) {
      console.error(e);
    }
  };

  const handleExcludeProduct = async (productId: number) => {
    try {
      await fetch('/api/v1/warehouse/pre-orders/exclude', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId }),
      });
      alert('Товар исключён из предзаказов');
      loadPreOrdersData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <div>
          <h2 className="page-title">Управление закупками</h2>
          <p className="text-muted" style={{ marginTop: '4px' }}>
            Контроль поставок, правила автозаказа, предзаказы
          </p>
        </div>
        <button className="btn btn-outline" onClick={syncAllData}>
          Обновить
        </button>
      </div>

      <OrdersTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {loading ? (
        <div className="loading-text">Загрузка...</div>
      ) : (
        <>
          {activeTab === 'active' && (
            <OrdersListContainer orders={activeOrders} emptyMessage="Нет активных поставок" />
          )}
          {activeTab === 'archived' && (
            <OrdersListContainer orders={archivedOrders} emptyMessage="Архив пуст" />
          )}
          {activeTab === 'preorder' && (
            <>
              <RuleCreatorBlock onRuleCreated={syncAllData} />
              <ActiveRulesList rules={rules} />
              <PreOrdersTable
                records={preOrders}
                onQuickOrder={handleQuickOrder}
                onExcludeProduct={handleExcludeProduct}
              />
            </>
          )}
        </>
      )}
    </div>
  );
};