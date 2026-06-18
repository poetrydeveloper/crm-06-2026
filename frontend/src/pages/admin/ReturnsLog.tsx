// frontend/src/pages/admin/ReturnsLog.tsx
import React, { useState, useEffect } from 'react';

interface LogRecord {
  service: string;
  level: string;
  message: string;
  operation_code: string;
  timestamp: string;
}

// 🔥 ВСТРОЕНО ИНЛАЙН ДЛЯ ЛИКВИДАЦИИ ОШИБКИ ИМПОРТА VITE
const LocalReturnsLogTable: React.FC<{ logs: LogRecord[] }> = ({ logs }) => {
  return (
    <div className="returns-log-table-container" style={{ background: '#1e1e1e', borderRadius: '6px', overflow: 'hidden' }}>
      <table style={{ width: 100 + '%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead style={{ background: '#2d2d2d', color: '#ffb74d' }}>
          <tr>
            <th style={{ padding: '12px' }}>Временная метка</th>
            <th style={{ padding: '12px' }}>Микросервис</th>
            <th style={{ padding: '12px' }}>Код</th>
            <th style={{ padding: '12px' }}>Лог-сообщение аудита</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ padding: '20px', color: '#888', textAlign: 'center' }}>
                Журнал пуст. Кассовых событий возврата не обнаружено.
              </td>
            </tr>
          ) : (
            logs.map((log, idx) => (
              <tr key={idx} className="payment-form-active" style={{ borderBottom: '1px solid #333' }}>
                <td style={{ padding: '12px', color: '#aaa' }}>{log.timestamp}</td>
                <td style={{ padding: '12px' }}>{log.service}</td>
                <td style={{ padding: '12px', color: '#ffb74d' }}>{log.operation_code}</td>
                <td style={{ padding: '12px' }}>{log.message}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export const ReturnsLog: React.FC = () => {
  const [logs, setLogs] = useState<LogRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const loadReturnsHistory = async () => {
    setLoading(true);
    try {
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
        <LocalReturnsLogTable logs={logs} />
      )}
    </div>
  );
};
