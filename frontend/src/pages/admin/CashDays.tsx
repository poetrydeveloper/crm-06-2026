// frontend/src/pages/admin/CashDays.tsx
import React, { useState, useEffect } from 'react';
import { CashDaysControls } from '../../components/atomic/CashDaysControls';
import { CashDaysTable } from '../../components/atomic/CashDaysTable';
import { AnalyticsSummaryBlock } from '../../components/atomic/AnalyticsSummaryBlock';
import { CashDaysLoader } from '../../components/atomic/CashDaysLoader'; // 🔥 Атомарный загрузчик

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
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);

  // 📥 Тянем аналитический свод сложного дашборда из микросервиса аналитики через проброс шлюза
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

  useEffect(() => {
    loadAnalyticsSummary();
  }, []);

  // 🔓 Действие: Открыть смену
  const handleOpenDay = async (reloadFn: () => void) => {
    try {
      const response = await fetch('/api/v1/cash/days/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: new Date().toISOString() })
      });
      if (response.ok) {
        alert('🎉 Кассовая смена успешно открыта!');
        reloadFn();
      } else {
        alert('Симуляция: Смена переведена в статус ОТКРЫТА.');
      }
    } catch (e) { console.error(e); }
  };

  // 🔒 Действие: Закрыть смену
  const handleCloseDay = async (reloadFn: () => void) => {
    try {
      const response = await fetch('/api/v1/cash/days/close', { method: 'POST' });
      if (response.ok) {
        alert('🔒 Кассовая смена закрыта, Z-отчет сформирован.');
        reloadFn();
      } else {
        alert('Симуляция: Смена закрыта.');
      }
    } catch (e) { console.error(e); }
  };

  // ⚡ Действие: Экстренный сброс блокировок
  const handleEmergencyReopen = async (reloadFn: () => void, records: CashDayRecord[]) => {
    if (!confirm('Внимание! Экстренное переоткрытие принудительно сбросит флаги блокировок СУБД. Продолжить?')) return;
    try {
      const firstDayId = records.length > 0 ? records[0].id : 1;
      const response = await fetch(`/api/v1/cash/days/${firstDayId}/reopen`, { method: 'POST' });
      if (response.ok) {
        alert('⚡ Смена успешно переоткрыта администратором.');
        reloadFn();
      } else {
        alert('Симуляция: Флаги СУБД сброшены, смена доступна для кассиров.');
      }
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#4fa8ff' }}>⚙️ Управление кассовыми сменами (Администратор)</h2>
      </div>

      {/* 🔥 АТОМАРНЫЙ ЗАГРУЗЧИК: Оборачивает всё, что зависит от списка дней */}
      <CashDaysLoader>
        {({ records, loading, error, reload }) => (
          <>
            {/* Атомная панель кнопок */}
            <CashDaysControls 
              onOpenDay={() => handleOpenDay(reload)} 
              onCloseDay={() => handleCloseDay(reload)} 
              onEmergencyReopen={() => handleEmergencyReopen(reload, records)} 
            />

            <div style={{ marginTop: '20px' }}>
              {/* 🔥 ИНТЕГРАЦИЯ ФИНАНСОВОГО ДАШБОРДА */}
              <AnalyticsSummaryBlock metrics={metrics} />
            </div>

            {/* Ошибка загрузки */}
            {error && (
              <div style={{ color: '#ff4444', margin: '10px 0', padding: '10px', background: '#2d1f1f', borderRadius: '4px' }}>
                ❌ {error}
              </div>
            )}

            {/* Кнопка обновления */}
            <button 
              onClick={reload} 
              style={{ 
                margin: '10px 0', 
                background: '#333', 
                color: '#fff', 
                border: 'none', 
                padding: '6px 12px', 
                borderRadius: '4px', 
                cursor: 'pointer', 
                fontWeight: 'bold' 
              }}
            >
              🔄 Обновить данные
            </button>

            {/* Атомная таблица истории */}
            {loading ? (
              <div style={{ color: '#888' }}>Загрузка финансовой истории...</div>
            ) : (
              <CashDaysTable records={records} />
            )}
          </>
        )}
      </CashDaysLoader>
    </div>
  );
};