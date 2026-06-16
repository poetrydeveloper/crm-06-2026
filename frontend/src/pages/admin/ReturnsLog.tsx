// frontend/src/pages/admin/ReturnsLog.tsx
import React, { useState, useEffect } from 'react';
import { ReturnsLogTable } from '../../components/atomic/ReturnsLogTable';

interface LogRecord {
  service: string;
  level: string;
  message: string;
  operation_code: string;
  timestamp: string;
}

export const ReturnsLog: React.FC = () => {
  const [logs, setLogs] = useState<LogRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const loadReturnsHistory = async () => {
    setLoading(true);
    try {
      // Запрашиваем данные логгера через роут шлюза
      const response = await fetch('/api/v1/logs/search?operation_code=0501');
      if (response.ok) {
        const data = await response.json();
        setLogs(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Ошибка загрузки журнала возвратов:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReturnsHistory();
  }, []);

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ margin: 0, color: '#ffb74d' }}>📋 Журнал Возвратов и Брака (Аудит Директора)</h2>
          <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#666' }}>
            Сквозной мониторинг дефектных партий и кассовых возвратов из микросервиса crm_logger_service
          </p>
        </div>
        <button 
          onClick={loadReturnsHistory} 
          style={{ background: '#333', color: '#fff', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          🔄 Обновить журнал
        </button>
      </div>

      {loading ? (
        <div style={{ color: '#888' }}>Вычитывание буфера логгера...</div>
      ) : (
        <ReturnsLogTable logs={logs} />
      )}
    </div>
  );
};
