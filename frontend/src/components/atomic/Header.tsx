// frontend/src/components/atomic/Header.tsx
import React from 'react';

export const Header: React.FC = () => {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      background: '#1e1e1e',
      color: '#fff',
      height: '60px',
      borderBottom: '1px solid #333'
    }}>
      <div style={{ fontOrder: 'bold', fontSize: '18px', color: '#4fa8ff' }}>
        ⚡ Lightweight CRM
      </div>
      <nav style={{ display: 'flex', gap: '20px' }}>
        <a href="/" style={{ color: '#fff', textDecoration: 'none' }}>🛒 Касса</a>
        <a href="/admin/catalog" style={{ color: '#fff', textDecoration: 'none' }}>⚙️ Админка</a>
        <a href="/warehouse/receipts" style={{ color: '#fff', textDecoration: 'none' }}>📦 Склад</a>
      </nav>
      <div style={{ fontSize: '14px', color: '#888' }}>
        Оператор: admin
      </div>
    </header>
  );
};
