// frontend/src/pages/admin/CashDays.tsx
import React, { useState, useEffect } from 'react';
import { CashDaysControls } from '../../components/atomic/CashDaysControls';
import { CashDaysTable } from '../../components/atomic/CashDaysTable';

interface CashDayRecord {
  id: number;
  created_at: string;
  status: 'ОТКРЫТА' | 'ЗАКРЫТА';
  total_sales: number;
}

export const CashDays: React.FC = () => {
  const [records, setRecords] = useState<CashDayRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // 📥 Тянем историю смен с бэкенда ядра
  const loadCashDays = async () => {
    try {
      const response = await fetch('/api/v1/cash/days');
      if (response.ok) {
        const data = await response.json();
        setRecords(Array.isArray(data) ? data : (data.days || data.data || []));
      }
    } catch (error) {
      console.error('Ошибка загрузки кассовых дней:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCashDays();
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
        loadCashDays();
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
        loadCashDays();
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
        loadCashDays();
      } else {
        alert('Симуляция: Флаги СУБД сброшены, смена доступна для кассиров.');
      }
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#4fa8ff' }}>⚙️ Управление кассовыми сменами (Администратор)</h2>
        <button onClick={loadCashDays} style={{ background: '#333', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>
          🔄 Обновить данные
        </button>
      </div>

      {/* Атомная панель кнопок */}
      <CashDaysControls 
        onOpenDay={handleOpenDay} 
        onCloseDay={handleCloseDay} 
        onEmergencyReopen={handleEmergencyReopen} 
      />

      {/* Атомная таблица */}
      {loading ? (
        <div style={{ color: '#888' }}>Загрузка финансовой истории...</div>
      ) : (
        <CashDaysTable records={records} />
      )}
    </div>
  );
};
