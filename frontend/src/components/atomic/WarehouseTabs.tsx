// frontend/src/components/atomic/WarehouseTabs.tsx
import React from 'react';

interface WarehouseTabsProps {
  activeTab: 'receipts' | 'suppliers';
  onTabChange: (tab: 'receipts' | 'suppliers') => void;
}

export const WarehouseTabs: React.FC<WarehouseTabsProps> = ({ activeTab, onTabChange }) => {
  return (
    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '1px solid #333', paddingBottom: '10px' }}>
      <button
        onClick={() => onTabChange('receipts')}
        style={{
          padding: '8px 16px',
          borderRadius: '4px',
          border: 'none',
          background: activeTab === 'receipts' ? '#4fa8ff' : '#2d2d2d',
          color: activeTab === 'receipts' ? '#000' : '#fff',
          fontWeight: 'bold',
          cursor: 'pointer'
        }}
      >
        📋 Активные поставки
      </button>
      <button
        onClick={() => onTabChange('suppliers')}
        style={{
          padding: '8px 16px',
          borderRadius: '4px',
          border: 'none',
          background: activeTab === 'suppliers' ? '#4fa8ff' : '#2d2d2d',
          color: activeTab === 'suppliers' ? '#000' : '#fff',
          fontWeight: 'bold',
          cursor: 'pointer'
        }}
      >
        🏢 Справочник поставщиков
      </button>
    </div>
  );
};
