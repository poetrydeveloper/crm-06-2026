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
    try {
      // 1. Считываем текущее состояние корзины из localStorage
      const currentCartRaw = localStorage.getItem('purchase_cart');
      const cartList = currentCartRaw ? JSON.parse(currentCartRaw) : [];

      // 2. Проверяем, нет ли уже этого товара в корзине, чтобы не дублировать строки
      const existingItemIdx = cartList.findIndex((item: any) => item.product_id === record.product_id);
      
      if (existingItemIdx > -1) {
        cartList[existingItemIdx].quantity += record.recommended_qty;
      } else {
        cartList.push({
          product_id: record.product_id,
          product_name: record.product_name,
          product_code: record.product_code,
          quantity: record.recommended_qty,
          estimated_purchase_price: record.estimated_purchase_price
        });
      }

      // 3. Сохраняем обновленный список обратно в буфер браузера
      localStorage.setItem('purchase_cart', JSON.stringify(cartList));
      
      alert(`🛒 Товар "${record.product_name}" (в количестве ${record.recommended_qty} шт.) успешно добавлен в корзину формирования общей заявки!\n\nПерейдите на вкладку "📦 Склад логистики" -> "Создать заявку", чтобы отправить заказ поставщику.`);
      
      // Исключаем позицию из текущего экрана предзаказов, чтобы визуально очистить витрину рисков
      setPreOrders(prev => prev.filter(p => p.pre_order_id !== record.pre_order_id));
    } catch (error) {
      console.error('Ошибка добавления товара в корзину снабжения:', error);
    }
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
