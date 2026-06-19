// frontend/src/pages/admin/CashDays.tsx
import React, { useState, useEffect } from 'react';
import { CashDaysControls } from '../../components/atomic/CashDaysControls';
import { CashDaysTable } from '../../components/atomic/CashDaysTable';
import { CashDaysLoader } from '../../components/atomic/CashDaysLoader';

interface CashDayRecord {
  id: number;
  created_at: string;
  status: 'ОТКРЫТА' | 'ЗАКРЫТА';
  total_sales: number;
}

export const CashDays: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleOpenDay = async (reloadFn: () => void) => {
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/cash/days/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: new Date().toISOString().split('T')[0] }),
      });
      const data = await response.json();
      if (response.ok) {
        alert(`Смена #${data.cash_day_id} открыта`);
        reloadFn();
      } else {
        alert(data.detail || 'Ошибка');
      }
    } catch (e) {
      console.error(e);
      alert('Ошибка сети');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCloseDay = async (reloadFn: () => void) => {
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/cash/days/close', { method: 'POST' });
      const data = await response.json();
      if (response.ok) {
        alert('Смена закрыта');
        reloadFn();
      } else {
        alert(data.detail || 'Ошибка');
      }
    } catch (e) {
      console.error(e);
      alert('Ошибка сети');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEmergencyReopen = async (reloadFn: () => void, records: CashDayRecord[]) => {
    if (!confirm('Экстренно переоткрыть смену?')) return;
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      const firstDayId = records.length > 0 ? records[0].id : 1;
      const response = await fetch(`/api/v1/cash/days/${firstDayId}/reopen`, { method: 'POST' });
      const data = await response.json();
      if (response.ok) {
        alert(`Смена #${firstDayId} переоткрыта`);
        reloadFn();
      } else {
        alert(data.detail || 'Ошибка');
      }
    } catch (e) {
      console.error(e);
      alert('Ошибка сети');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h2 className="page-title">Управление кассовыми сменами</h2>
      </div>

      <CashDaysLoader>
        {({ records, loading, error, reload }) => (
          <>
            <CashDaysControls
              onOpenDay={() => handleOpenDay(reload)}
              onCloseDay={() => handleCloseDay(reload)}
              onEmergencyReopen={() => handleEmergencyReopen(reload, records)}
            />

            {error && <div className="alert alert-danger">{error}</div>}

            <div className="d-flex justify-between align-center mb-3">
              <span className="text-muted">Всего смен: {records.length}</span>
              <button className="btn btn-outline btn-sm" onClick={reload}>
                Обновить
              </button>
            </div>

            {loading ? (
              <div className="loading-text">Загрузка...</div>
            ) : (
              <CashDaysTable records={records} />
            )}
          </>
        )}
      </CashDaysLoader>
    </div>
  );
};