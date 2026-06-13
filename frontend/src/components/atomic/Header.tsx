// frontend/src/components/atomic/Header.tsx
import React from 'react';

export const Header: React.FC = () => {
  // Функция для SPA навигации без перезагрузки всей страницы
  const navigateTo = (e: React.MouseEvent<HTMLButtonElement>, path: string) => {
    e.preventDefault();
    window.history.pushState({}, '', path);
    // Триггерим событие, чтобы App.tsx поймал смену адреса
    window.dispatchEvent(new Event('popstate'));
  };

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
      <div style={{ fontWeight: 'bold', fontSize: '18px', color: '#4fa8ff' }}> {/* Исправлено с fontOrder */}
        ⚡ Lightweight CRM
      </div>
      <nav style={{ display: 'flex', gap: '20px' }}>
        <button 
          onClick={(e) => navigateTo(e, '/')} 
          style={{ background: 'none', border: 'none', color: '#fff', fontSize: '16px', cursor: 'pointer' }}
        >
          🛒 Касса
        </button>
        <button 
          onClick={(e) => navigateTo(e, '/admin/catalog')} 
          style={{ background: 'none', border: 'none', color: '#fff', fontSize: '16px', cursor: 'pointer' }}
        >
          ⚙️ Админка
        </button>
        <button 
          onClick={(e) => navigateTo(e, '/warehouse/receipts')} 
          style={{ background: 'none', border: 'none', color: '#fff', fontSize: '16px', cursor: 'pointer' }}
        >
          📦 Склад
        </button>
      </nav>
      <div style={{ fontSize: '14px', color: '#888' }}>
        Оператор: admin
      </div>
    </header>
  );
};
