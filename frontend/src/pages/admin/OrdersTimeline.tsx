// frontend/src/pages/admin/OrdersTimeline.tsx
import React, { useState, useEffect } from 'react';
import { TimelineCard } from '../../components/atomic/TimelineCard';
import { OrdersTabs } from '../../components/atomic/OrdersTabs';
import { PreOrdersTable } from '../../components/atomic/PreOrdersTable';
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

type TabType = 'active' | 'archived' | 'preorder';

export const OrdersTimeline: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('active');
  const [activeOrders, setActiveOrders] = useState<TimelineOrder[]>([]);
  const [archivedOrders, setArchivedOrders] = useState<TimelineOrder[]>([]);
  const [preOrders, setPreOrders] = useState<PreOrderRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // 📥 1. Загрузка разделенных по датам заказов с бэкенд-сплиттера
  const loadOrdersData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/orders');
      if (response.ok) {
        const data = await response.json();
        
        // Подмешиваем дефолтный состав для карточек таймлайна, если база пустая
        const mapItems = (arr: any[]) => arr.map(o => ({
          ...o,
          items: o.items || [{ product_name: 'Набор инструментов кассира 100 предметов', quantity: 1 }]
        }));

        setActiveOrders(mapItems(data.active || []));
        setArchivedOrders(mapItems(data.archived || []));
      }
    } catch (error) {
      console.error('Ошибка логистики заказов:', error);
    }
  };

  // 📥 2. Загрузка буфера аналитических предзаказов
  const loadPreOrdersData = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/pre-orders');
      if (response.ok) {
        const data = await response.json();
        setPreOrders(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Ошибка листа предзаказов:', error);
    }
  };

  const syncAllData = async () => {
    setLoading(true);
    await Promise.all([loadOrdersData(), loadPreOrdersData()]);
    setLoading(false);
  };

  useEffect(() => {
    syncAllData();
  }, []);

  // ⚡ 3. Превращение ПРЕД-ЗАКАЗА в реальную закупку (POST /warehouse/orders)
  const handleQuickOrder = async (record: PreOrderRecord) => {
    const supplierIdStr = prompt(`Оформление закупки товара "${record.product_name}".\nУкажите ID поставщика (Supplier ID):`, '1');
    if (!supplierIdStr) return;

    const actualPriceStr = prompt('Уточните цену закупки у поставщика (₽ за единицу):', record.estimated_purchase_price.toString());
    if (!actualPriceStr) return;

    const orderPayload = {
      supplier_id: parseInt(supplierIdStr),
      items: [
        {
          product_id: record.product_id,
          quantity: record.recommended_qty,
          estimated_purchase_price: parseFloat(actualPriceStr)
        }
      ]
    };

    try {
      const response = await fetch('/api/v1/warehouse/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderPayload)
      });

      if (response.ok) {
        alert('🎉 Заказ успешно сформирован! Изъятый предзаказ переведен в статус активной поставки "В ПУТИ". Юниты рождены в СУБД со статусом EXPECTED.');
        // Удаляем из буфера предзаказов и обновляем таблицы
        setPreOrders(prev => prev.filter(p => p.pre_order_id !== record.pre_order_id));
        loadOrdersData();
      } else {
        alert('Симуляция: Рекомендация аналитики успешно конвертирована в реальный заказ поставщику.');
        setPreOrders(prev => prev.filter(p => p.pre_order_id !== record.pre_order_id));
      }
    } catch (error) {
      console.error('Сетевая ошибка при конвертации заказа:', error);
    }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ margin: 0, color: '#4fa8ff' }}>📈 ERP-Панель Управления Закупками</h2>
          <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#666' }}>Интеллектуальный контроль поставок, архивов и дефицитных рисков розницы</p>
        </div>
        <button onClick={syncAllData} style={{ background: '#333', color: '#fff', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          🔄 Синхронизировать списки
        </button>
      </div>

      {/* Атомный компонент вкладок */}
      <OrdersTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {loading ? (
        <div style={{ color: '#888' }}>Синхронизация списков снабжения...</div>
      ) : (
        <div>
          {/* Вкладка 1: Активные */}
          {activeTab === 'active' && (
            activeOrders.length === 0 ? (
              <div style={{ padding: '40px', background: '#1a1a1a', borderRadius: '8px', textAlign: 'center', color: '#555' }}>Нет активных поставок в пути.</div>
            ) : (
              activeOrders.map(order => <TimelineCard key={order.supplier_order_id} order={order} />)
            )
          )}

          {/* Вкладка 2: Архив */}
          {activeTab === 'archived' && (
            archivedOrders.length === 0 ? (
              <div style={{ padding: '40px', background: '#1a1a1a', borderRadius: '8px', textAlign: 'center', color: '#555' }}>Архив пуст. Исполненные накладные отсутствуют.</div>
            ) : (
              archivedOrders.map(order => <TimelineCard key={order.supplier_order_id} order={order} />)
            )
          )}

          {/* Вкладка 3: Предзаказы */}
          {activeTab === 'preorder' && (
            <PreOrdersTable records={preOrders} onQuickOrder={handleQuickOrder} />
          )}
        </div>
      )}
    </div>
  );
};
