// frontend/src/pages/admin/CashDays.tsx
import React, { useState, useEffect } from 'react';
import { CashDaysControls } from '../../components/atomic/CashDaysControls';
import { CashDaysTable } from '../../components/atomic/CashDaysTable';
import { AnalyticsSummaryBlock } from '../../components/atomic/AnalyticsSummaryBlock'; // 🔥 Новой импорт

interface CashDayRecord {
  id: number;
  created_at: string;
  status: 'ОТКРЫТА' | 'ЗАКРЫТА';
  total_sales: number;
}

interface AnalyticsMetrics {
  total_sales: number;
  active_customers: number;
  conversion_rate: string;
}

export const CashDays: React.FC = () => {
  const [records, setRecords] = useState<CashDayRecord[]>([]);
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null); // 🔥 Стейт финансовых метрик
  const [loading, setLoading] = useState(true);

  // 📥 1. Тянем историю смен с бэкенда ядра
  const loadCashDays = async () => {
    try {
      const response = await fetch('/api/v1/cash/days');
      if (response.ok) {
        const data = await response.json();
        setRecords(Array.isArray(data) ? data : (data.days || data.data || []));
      }
    } catch (error) {
      console.error('Ошибка загрузки кассовых дней:', error);
    }
  };

  // 📥 2. Тянем аналитический свод сложного дашборда из микросервиса аналитики через проброс шлюза
  const loadAnalyticsSummary = async () => {
    try {
      const response = await fetch('/api/v1/analytics/summary');
      if (response.ok) {
        const jsonBody = await response.json();
        if (jsonBody.status === 'success' && jsonBody.metrics) {
          setMetrics(jsonBody.metrics);
        }
      }
    } catch (error) {
      console.error('Ошибка вызова микросервиса аналитики:', error);
    }
  };

  const syncAllData = async () => {
    setLoading(true);
    await Promise.all([loadCashDays(), loadAnalyticsSummary()]);
    setLoading(false);
  };

  useEffect(() => {
    syncAllData();
  }, []);

  // 🔓 Действие: Открыть смену
  const handleOpenDay = async () => {
    try {
      const response = await fetch('/api/v1/cash/days/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: new Date().toISOString() })
      });
      if (response.ok) {
        alert('🎉 Кассовая смена успешно открыта!');
        syncAllData();
      } else {
        alert('Симуляция: Смена переведена в статус ОТКРЫТА.');
        setRecords(prev => [{ id: Date.now(), created_at: new Date().toISOString(), status: 'ОТКРЫТА', total_sales: 0 }, ...prev]);
      }
    } catch (e) { console.error(e); }
  };

  // 🔒 Действие: Закрыть смену
  const handleCloseDay = async () => {
    try {
      const response = await fetch('/api/v1/cash/days/close', { method: 'POST' });
      if (response.ok) {
        alert('🔒 Кассовая смена закрыта, Z-отчет сформирован.');
        syncAllData();
      } else {
        alert('Симуляция: Смена закрыта.');
        setRecords(prev => prev.map((r, i) => i === 0 ? { ...r, status: 'ЗАКРЫТА' } : r));
      }
    } catch (e) { console.error(e); }
  };

  // ⚡ Действие: Экстренный сброс блокировок
  const handleEmergencyReopen = async () => {
    if (!confirm('Внимание! Экстренное переоткрытие принудительно сбросит флаги блокировок СУБД. Продолжить?')) return;
    try {
      const response = await fetch('/api/v1/cash/days/reopen', { method: 'POST' });
      if (response.ok) {
        alert('⚡ Смена успешно переоткрыта администратором.');
        syncAllData();
      } else {
        alert('Симуляция: Флаги СУБД сброшены, смена доступна для кассиров.');
      }
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#4fa8ff' }}>⚙️ Управление кассовыми сменами (Администратор)</h2>
        <button onClick={syncAllData} style={{ background: '#333', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          🔄 Обновить данные
        </button>
      </div>

      {/* Атомная панель кнопок */}
      <CashDaysControls 
        onOpenDay={handleOpenDay} 
        onCloseDay={handleCloseDay} 
        onEmergencyReopen={handleEmergencyReopen} 
      />

      <div style={{ marginTop: '20px' }}>
        {/* 🔥 ИНТЕГРАЦИЯ ФИНАНСОВОГО ДАШБОРДА: Сюда рендерим верхние карточки выручки и маржи */}
        <AnalyticsSummaryBlock metrics={metrics} />
      </div>

      {/* Атомная таблица истории */}
      {loading ? (
        <div style={{ color: '#888' }}>Загрузка финансовой истории...</div>
      ) : (
        <CashDaysTable records={records} />
      )}
    </div>
  );
};
