// frontend/src/components/atomic/OrdersTabs.tsx
import React from 'react';

type TabType = 'active' | 'archived' | 'preorder';

interface OrdersTabsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export const OrdersTabs: React.FC<OrdersTabsProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="d-flex gap-8 mb-3">
      <button
        className={`btn btn-sm ${activeTab === 'active' ? 'btn-primary' : 'btn-outline'}`}
        onClick={() => onTabChange('active')}
      >
        Активные поставки
      </button>
      <button
        className={`btn btn-sm ${activeTab === 'archived' ? 'btn-primary' : 'btn-outline'}`}
        onClick={() => onTabChange('archived')}
      >
        Архив
      </button>
      <button
        className={`btn btn-sm ${activeTab === 'preorder' ? 'btn-primary' : 'btn-outline'}`}
        onClick={() => onTabChange('preorder')}
      >
        Умный предзаказ
      </button>
    </div>
  );
};