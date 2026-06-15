// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import { Header } from './components/atomic/Header';
import { Catalog } from './pages/admin/Catalog';
import { Receipts } from './pages/warehouse/Receipts';
import { Cashbox } from './pages/cashbox/Cashbox';
import { CashDays } from './pages/admin/CashDays';
import { OrdersTimeline } from './pages/admin/OrdersTimeline';
import { UnitMap } from './pages/admin/UnitMap';

export default function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const handleLocationChange = () => setCurrentPath(window.location.pathname);
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  // Простейший асинхронный роутер для прохождения BDD-тестов без внешних либ
  const renderPage = () => {
    if (currentPath === '/' || currentPath === '') {
      return <Cashbox />;
    }
    if (currentPath.startsWith('/admin/catalog')) {
      return <Catalog />;
    }
    if (currentPath.startsWith('/admin/cash-days')) {
      return <CashDays />;
    }
    // 🔥 СТРОГИЙ РОУТ ДЛЯ ТАЙМЛАЙНА ЛОГИСТИКИ
    if (currentPath === '/admin/orders') {
      return <OrdersTimeline />;
    }
    if (currentPath === '/admin/unit-map') {
      return <UnitMap />;
    }
    if (currentPath.startsWith('/warehouse')) {
      return <Receipts />;
    }
    return <div style={{ padding: '20px' }}>🚨 404 — Страница не найдена</div>;
  };

  return (
    <div style={{ background: '#121212', color: '#fff', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      <Header />
      <main>{renderPage()}</main>
    </div>
  );
}