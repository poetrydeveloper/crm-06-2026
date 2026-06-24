// frontend/src/components/atomic/Header.tsx
import React from 'react';

export const Header: React.FC = () => {
  const currentPath = window.location.pathname;

  const navigateTo = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('popstate'));
  };

  const isActive = (path: string) => currentPath === path || (path !== '/' && currentPath.startsWith(path));

  const navItems = [
    { path: '/', label: '🛒 Касса' },
    { path: '/admin/catalog', label: '🗂️ Каталог' },
    { path: '/admin/cash-days', label: '⚙️ Смены' },
    { path: '/admin/orders', label: '📈 Логистика' },
    { path: '/admin/unit-map', label: '🔍 Аудит' },
    { path: '/admin/returns', label: '🔄 Возвраты' },
    { path: '/admin/returns-log', label: '📋 Журнал' },
    { path: '/warehouse', label: '📦 Склад' },
    // 🔥 НОВЫЕ ПУНКТЫ ДЛЯ УПРАВЛЕНИЯ АВТОЗАКУПКАМИ И СНАБЖЕНИЕМ
    { path: '/supply/rules', label: '⚙️ Правила закупки' },
    { path: '/supply/report', label: '📊 Отчет дефицита' },
  ];

  return (
    <header className="navbar">
      <div className="navbar-brand" onClick={() => navigateTo('/')}>
        🛠️ Lightweight CRM
      </div>
      <nav className="navbar-nav">
        {navItems.map(item => (
          <button
            key={item.path}
            className={`navbar-item ${isActive(item.path) ? 'active' : ''}`}
            onClick={() => navigateTo(item.path)}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <div className="navbar-version">v1.0.26</div>
    </header>
  );
};
