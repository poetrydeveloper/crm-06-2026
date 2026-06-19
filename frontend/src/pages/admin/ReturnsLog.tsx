// frontend/src/pages/admin/ReturnsLog.tsx
import React, { useState, useEffect } from 'react';

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
      const response = await fetch('/api/v1/logs/search?operation_code=0501');
      if (response.ok) {
        const data = await response.json();
        setLogs(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Ошибка загрузки журнала:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReturnsHistory();
  }, []);

  return (
    <div className="page-content">
      <div className="page-header">
        <div>
          <h2 className="page-title">Журнал возвратов и брака</h2>
          <p className="text-muted" style={{ marginTop: '4px' }}>
            Аудит операций возврата из crm_logger_service
          </p>
        </div>
        <button className="btn btn-outline" onClick={loadReturnsHistory}>
          Обновить
        </button>
      </div>

      {loading ? (
        <div className="loading-text">Загрузка журнала...</div>
      ) : (
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th>Время</th>
                <th>Сервис</th>
                <th>Код</th>
                <th>Сообщение</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="empty-row">Журнал пуст</td>
                </tr>
              ) : (
                logs.map((log, idx) => (
                  <tr key={idx}>
                    <td className="text-muted" style={{ whiteSpace: 'nowrap' }}>{log.timestamp}</td>
                    <td>{log.service}</td>
                    <td>
                      <span className="badge badge-warning">{log.operation_code}</span>
                    </td>
                    <td>{log.message}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};