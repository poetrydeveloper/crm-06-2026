// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import { Header } from './components/atomic/Header';
import { Catalog } from './pages/admin/Catalog';
import { Receipts } from './pages/warehouse/Receipts';
import { Cashbox } from './pages/cashbox/Cashbox';

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
    if (currentPath.startsWith('/admin')) {
      return <Catalog />;
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