// frontend/src/components/atomic/CashDaysTable.tsx
import React from 'react';

interface CashDayRecord {
  id: number;
  created_at: string;
  status: 'ОТКРЫТА' | 'ЗАКРЫТА';
  total_sales: number;
}

interface CashDaysTableProps {
  records: CashDayRecord[];
}

export const CashDaysTable: React.FC<CashDaysTableProps> = ({ records }) => {
  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            <th>ID смены</th>
            <th>Дата открытия</th>
            <th>Статус</th>
            <th style={{ textAlign: 'right' }}>Выручка</th>
          </tr>
        </thead>
        <tbody>
          {records.length === 0 ? (
            <tr>
              <td colSpan={4} className="empty-row">История кассовых смен пуста</td>
            </tr>
          ) : (
            records.map((record) => (
              <tr key={record.id}>
                <td style={{ fontWeight: 600 }}>#{record.id}</td>
                <td className="text-muted">{new Date(record.created_at).toLocaleDateString('ru-RU')}</td>
                <td>
                  <span className={`badge ${record.status === 'ОТКРЫТА' ? 'badge-success' : 'badge-secondary'}`}>
                    {record.status}
                  </span>
                </td>
                <td style={{ textAlign: 'right', fontWeight: 700, color: 'var(--success)' }}>
                  {record.total_sales.toFixed(2)} ₽
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};