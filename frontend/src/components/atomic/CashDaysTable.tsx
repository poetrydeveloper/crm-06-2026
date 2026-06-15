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
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
        <thead>
          <tr style={{ background: '#222', borderBottom: '2px solid #333', textAlign: 'left' }}>
            <th style={{ padding: '12px' }}>ID Смены</th>
            <th style={{ padding: '12px' }}>Дата Открытия</th>
            <th style={{ padding: '12px' }}>Текущий Статус</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Выручка (Финансовый Итог)</th>
          </tr>
        </thead>
        <tbody>
          {records.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ padding: '24px', textAlign: 'center', color: '#666' }}>
                📭 История кассовых смен пуста.
              </td>
            </tr>
          ) : (
            records.map(record => (
              <tr key={record.id} style={{ borderBottom: '1px solid #333' }}>
                <td style={{ padding: '12px', fontWeight: 'bold' }}>#{record.id}</td>
                <td style={{ padding: '12px', color: '#aaa' }}>
                  {new Date(record.created_at).toLocaleDateString('ru-RU')}
                </td>
                <td style={{ padding: '12px' }}>
                  <span style={{ 
                    background: record.status === 'ОТКРЫТА' ? '#1b5e20' : '#2d2d2d', 
                    padding: '4px 10px', 
                    borderRadius: '4px', 
                    fontSize: '12px', 
                    fontWeight: 'bold',
                    color: record.status === 'ОТКРЫТА' ? '#a5d6a7' : '#aaa' 
                  }}>
                    ● {record.status}
                  </span>
                </td>
                <td style={{ padding: '12px', textAlign: 'right', fontWeight: 'bold', color: '#2ea44f' }}>
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
