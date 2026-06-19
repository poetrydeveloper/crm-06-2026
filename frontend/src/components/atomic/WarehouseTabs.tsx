// frontend/src/components/atomic/WarehouseTabs.tsx
import React from 'react';

interface WarehouseTabsProps {
  activeTab: 'receipts' | 'suppliers';
  onTabChange: (tab: 'receipts' | 'suppliers') => void;
}

export const WarehouseTabs: React.FC<WarehouseTabsProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="d-flex gap-8">
      <button
        className={`btn btn-sm ${activeTab === 'receipts' ? 'btn-primary' : 'btn-outline'}`}
        onClick={() => onTabChange('receipts')}
      >
        Активные поставки
      </button>
      <button
        className={`btn btn-sm ${activeTab === 'suppliers' ? 'btn-primary' : 'btn-outline'}`}
        onClick={() => onTabChange('suppliers')}
      >
        Поставщики
      </button>
    </div>
  );
};