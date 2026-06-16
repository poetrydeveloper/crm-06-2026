// frontend/src/components/atomic/Header.tsx
import React from 'react';

export const Header: React.FC = () => {
  const currentPath = window.location.pathname;

  // Функция умного SPA-перехода без перезагрузки страницы
  const navigateTo = (path: string) => {
    window.history.pushState({}, '', path);
    // Генерируем кастомное событие, чтобы App.tsx мгновенно перерисовал страницу
    window.dispatchEvent(new Event('popstate'));
  };

  const linkStyle = (path: string) => ({
    background: currentPath === path ? '#333' : 'transparent',
    color: currentPath === path ? '#4fa8ff' : '#fff',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold' as const,
    fontSize: '14px',
    outline: 'none',
    display: 'flex',
    alignItems: 'center',
    gap: '6px'
  });

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      background: '#1a1a1a',
      height: '60px',
      borderBottom: '1px solid #333'
    }}>
      {/* Логотип системы */}
      <div 
        onClick={() => navigateTo('/')} 
        style={{ fontSize: '18px', fontWeight: 'bold', color: '#4fa8ff', cursor: 'pointer' }}
      >
        🛠️ Lightweight CRM
      </div>

      {/* Панель навигационных кнопок */}
      <nav style={{ display: 'flex', gap: '10px' }}>
        <button onClick={() => navigateTo('/')} style={linkStyle('/')}>🛒 Живая касса</button>
        <button onClick={() => navigateTo('/admin/catalog')} style={linkStyle('/admin/catalog')}>🗂️ Каталог (Админ)</button>
        <button onClick={() => navigateTo('/admin/cash-days')} style={linkStyle('/admin/cash-days')}>⚙️ Смены (Админ)</button>
        <button onClick={() => navigateTo('/admin/orders')} style={linkStyle('/admin/orders')}>📈 Логистика (Админ)</button>
        <button onClick={() => navigateTo('/admin/unit-map')} style={linkStyle('/admin/unit-map')}>🔍 Аудит Юнитов (Админ)</button>
        <button onClick={() => navigateTo('/admin/returns')} style={linkStyle('/admin/returns')}>🔄 Возвраты (Админ)</button>
        <button onClick={() => navigateTo('/admin/returns-log')} style={linkStyle('/admin/returns-log')}>📋 Журнал Брака (Админ)</button>
        <button onClick={() => navigateTo('/warehouse')} style={linkStyle('/warehouse')}>📦 Склад логистики</button>
      </nav>


      {/* Правая часть (Системное время или индикатор робота) */}
      <div style={{ fontSize: '12px', color: '#666', fontWeight: 'bold' }}>
        v1.0.26 ● QA ACTIVE
      </div>
    </header>
  );
};
