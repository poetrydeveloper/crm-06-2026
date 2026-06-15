// frontend/src/components/atomic/OrdersTabs.tsx
import React from 'react';

type TabType = 'active' | 'archived' | 'preorder';

interface OrdersTabsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export const OrdersTabs: React.FC<OrdersTabsProps> = ({ activeTab, onTabChange }) => {
  const btnStyle = (tab: TabType) => ({
    padding: '8px 16px',
    borderRadius: '4px',
    border: 'none',
    background: activeTab === tab ? '#4fa8ff' : '#2d2d2d',
    color: activeTab === tab ? '#000' : '#fff',
    fontWeight: 'bold' as const,
    cursor: 'pointer'
  });

  return (
    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '1px solid #333', paddingBottom: '12px' }}>
      <button onClick={() => onTabChange('active')} style={btnStyle('active')}>
        🚚 Активные поставки (В пути)
      </button>
      <button onClick={() => onTabChange('archived')} style={btnStyle('archived')}>
        🗄️ Архив закупок (Исполнены)
      </button>
      <button onClick={() => onTabChange('preorder')} style={btnStyle('preorder')}>
        💡 Умный предзаказ (Аналитика)
      </button>
    </div>
  );
};
