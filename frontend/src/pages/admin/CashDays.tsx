// frontend/src/pages/admin/CashDays.tsx
import React, { useState, useEffect } from 'react';
import { CashDaysControls } from '../../components/atomic/CashDaysControls';
import { CashDaysTable } from '../../components/atomic/CashDaysTable';
import { AnalyticsSummaryBlock } from '../../components/atomic/AnalyticsSummaryBlock';
import { CashDaysLoader } from '../../components/atomic/CashDaysLoader';

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

// 🛎️ Вспомогательная функция для браузерных уведомлений
const notify = (title: string, body: string) => {
  if (Notification.permission === "granted") {
    new Notification(title, { body });
  }
};

export const CashDays: React.FC = () => {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);
  const [isProcessing, setIsProcessing] = useState(false); // 🔒 Защита от двойного клика

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
    // 🛎️ Запрашиваем разрешение на уведомления при первом заходе
    if (Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  // 🔓 Действие: Открыть смену
  const handleOpenDay = async (reloadFn: () => void) => {
    if (isProcessing) return; // 🔒 Защита от двойного клика
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/cash/days/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: new Date().toISOString().split('T')[0] })
      });
      const data = await response.json();
      
      if (response.ok) {
        notify("🟢 Кассовая смена открыта", `Смена #${data.cash_day_id} успешно открыта!`);
        reloadFn();
      } else {
        alert(data.detail || 'Ошибка открытия смены');
      }
    } catch (e) { 
      console.error(e);
      alert('Ошибка сети при открытии смены');
    } finally {
      setIsProcessing(false);
    }
  };

  // 🔒 Действие: Закрыть смену
  const handleCloseDay = async (reloadFn: () => void) => {
    if (isProcessing) return; // 🔒 Защита от двойного клика
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/cash/days/close', { method: 'POST' });
      const data = await response.json();
      
      if (response.ok) {
        notify("🔴 Кассовая смена закрыта", data.message || "Z-отчет сформирован!");
        reloadFn();
      } else {
        alert(data.detail || 'Ошибка закрытия смены');
      }
    } catch (e) { 
      console.error(e);
      alert('Ошибка сети при закрытии смены');
    } finally {
      setIsProcessing(false);
    }
  };

  // ⚡ Действие: Экстренный сброс блокировок
  const handleEmergencyReopen = async (reloadFn: () => void, records: CashDayRecord[]) => {
    if (!confirm('Внимание! Экстренное переоткрытие принудительно сбросит флаги блокировок СУБД. Продолжить?')) return;
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      const firstDayId = records.length > 0 ? records[0].id : 1;
      const response = await fetch(`/api/v1/cash/days/${firstDayId}/reopen`, { method: 'POST' });
      const data = await response.json();
      
      if (response.ok) {
        notify("⚡ Экстренное переоткрытие", `Смена #${firstDayId} переоткрыта администратором!`);
        reloadFn();
      } else {
        alert(data.detail || 'Ошибка переоткрытия смены');
      }
    } catch (e) { 
      console.error(e);
      alert('Ошибка сети при переоткрытии смены');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#4fa8ff' }}>⚙️ Управление кассовыми сменами (Администратор)</h2>
      </div>

      <CashDaysLoader>
        {({ records, loading, error, reload }) => (
          <>
            <CashDaysControls 
              onOpenDay={() => handleOpenDay(reload)} 
              onCloseDay={() => handleCloseDay(reload)} 
              onEmergencyReopen={() => handleEmergencyReopen(reload, records)} 
            />

            <div style={{ marginTop: '20px' }}>
              <AnalyticsSummaryBlock metrics={metrics} />
            </div>

            {error && (
              <div style={{ color: '#ff4444', margin: '10px 0', padding: '10px', background: '#2d1f1f', borderRadius: '4px' }}>
                ❌ {error}
              </div>
            )}

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