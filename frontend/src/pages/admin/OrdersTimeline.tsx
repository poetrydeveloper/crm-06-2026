// frontend/src/pages/admin/OrdersTimeline.tsx
import React, { useState, useEffect } from 'react';
import { OrdersTabs } from '../../components/atomic/OrdersTabs';
import { PreOrdersTable } from '../../components/atomic/PreOrdersTable';
import { RuleCreatorBlock } from '../../components/atomic/RuleCreatorBlock';
import { ActiveRulesList } from '../../components/atomic/ActiveRulesList';
import { OrdersListContainer } from '../../components/atomic/OrdersListContainer';
import type { PreOrderRecord } from '../../components/atomic/PreOrdersTable';

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
        const mapItems = (arr: any[]) => arr.map(o => ({
          ...o,
          items: o.items || [{ product_name: 'Набор инструментов кассира 100 предметов', quantity: 1 }]
        }));
        setActiveOrders(mapItems(data.active || []));
        setArchivedOrders(mapItems(data.archived || []));
      }
    } catch (error) { console.error(error); }
  };

  const loadPreOrdersData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/pre-orders');
      if (response.ok) {
        const data = await response.json();
        setPreOrders(Array.isArray(data) ? data : []);
      }
    } catch (error) { console.error(error); }
  };

  const loadRulesData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/purchase-rules');
      if (response.ok) {
        const data = await response.json();
        setRules(Array.isArray(data) ? data : []);
      }
    } catch (error) { console.error(error); }
  };

  const syncAllData = async () => {
    setLoading(true);
    await Promise.all([loadOrdersData(), loadPreOrdersData(), loadRulesData()]);
    setLoading(false);
  };

  useEffect(() => { syncAllData(); }, []);

  const handleQuickOrder = async (record: PreOrderRecord) => {
    const supplierIdStr = prompt(`Закупка "${record.product_name}".\nID поставщика:`, '1');
    if (!supplierIdStr) return;
    const actualPriceStr = prompt('Цена закупки (₽):', record.estimated_purchase_price.toString());
    if (!actualPriceStr) return;

    try {
      const response = await fetch('/api/v1/warehouse/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_id: parseInt(supplierIdStr),
          items: [{ product_id: record.product_id, quantity: record.recommended_qty, estimated_purchase_price: parseFloat(actualPriceStr) }]
        })
      });
      if (response.ok) {
        alert('🎉 Заказ сформирован! Рекомендация переведена в статус активной поставки "В ПУТИ".');
        syncAllData();
      }
    } catch (error) { console.error(error); }
  };

  const handleExcludeProduct = async (productId: number) => {
    try {
      const response = await fetch('/api/v1/warehouse/pre-orders/exclude', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
      });
      if (response.ok) {
        alert('🚫 Товар успешно забанен в предзаказах!');
        loadPreOrdersData();
      }
    } catch (error) { console.error(error); }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ margin: 0, color: '#4fa8ff' }}>📈 ERP-Панель Управления Закупками</h2>
          <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#666' }}>Интеллектуальный контроль поставок, активных правил и черных списков СУБД</p>
        </div>
        <button onClick={syncAllData} style={{ background: '#333', color: '#fff', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          🔄 Синхронизировать
        </button>
      </div>

      <OrdersTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {loading ? (
        <div style={{ color: '#888' }}>Синхронизация списков...</div>
      ) : (
        <div>
          {activeTab === 'active' && (
            <OrdersListContainer orders={activeOrders} emptyMessage="Нет активных поставок в пути. Воспользуйтесь умными предзаказами." />
          )}

          {activeTab === 'archived' && (
            <OrdersListContainer orders={archivedOrders} emptyMessage="Архив пуст. Исполненные накладные отсутствуют." />
          )}

          {activeTab === 'preorder' && (
            <div>
              <RuleCreatorBlock onRuleCreated={syncAllData} />
              <ActiveRulesList rules={rules} />
              <PreOrdersTable records={preOrders} onQuickOrder={handleQuickOrder} onExcludeProduct={handleExcludeProduct} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
