// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import { Header } from './components/atomic/Header';
import { Catalog } from './pages/admin/Catalog';
import { Receipts } from './pages/warehouse/Receipts';
import { Cashbox } from './pages/cashbox/Cashbox';
import { CashDays } from './pages/admin/CashDays';
import { OrdersTimeline } from './pages/admin/OrdersTimeline';
import { UnitMap } from './pages/admin/UnitMap';
import { Returns } from './pages/cashbox/Returns';
import { ReturnsLog } from './pages/admin/ReturnsLog';

// 🔥 ИМПОРТ НОВЫХ СТРАНИЦ УПРАВЛЕНИЯ СНАБЖЕНИЕМ И АВТОЗАКАЗАМИ
import { PurchaseRules } from './pages/warehouse/PurchaseRules';
import { SupplyReport } from './pages/warehouse/SupplyReport';

export default function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const handleLocationChange = () => setCurrentPath(window.location.pathname);
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

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
    if (currentPath === '/admin/orders') {
      return <OrdersTimeline />;
    }
    if (currentPath === '/admin/unit-map') {
      return <UnitMap />;
    }
    if (currentPath === '/admin/returns') {
      return <Returns />;
    }
    if (currentPath === '/admin/returns-log') {
      return <ReturnsLog />;
    }
    
    // 🔥 НОВЫЙ РАЗДЕЛ: АНАЛИТИКА И МАТРИЦА АВТОСНАБЖЕНИЯ
    if (currentPath === '/supply/rules') {
      return <PurchaseRules />;
    }
    if (currentPath === '/supply/report') {
      return <SupplyReport />;
    }
    
    if (currentPath.startsWith('/warehouse')) {
      return <Receipts />;
    }
    return (
      <div className="page-content">
        <div className="alert alert-warning">🚨 404 — Страница не найдена</div>
      </div>
    );
  };

  return (
    <>
      <Header />
      <main className="container">{renderPage()}</main>
    </>
  );
}
