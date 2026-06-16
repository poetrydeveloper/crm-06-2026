// frontend/src/components/atomic/AnalyticsSummaryBlock.tsx
import React from 'react';

interface Metrics {
  total_sales: number;
  active_customers: number;
  conversion_rate: string;
}

interface AnalyticsSummaryBlockProps {
  metrics: Metrics | null;
}

export const AnalyticsSummaryBlock: React.FC<AnalyticsSummaryBlockProps> = ({ metrics }) => {
  if (!metrics) {
    return (
      <div style={{ padding: '15px', background: '#1a1a1a', borderRadius: '6px', border: '1px solid #333', color: '#666', fontSize: '13px', marginBottom: '20px' }}>
        ⏳ Вычисление операционных финансовых показателей сети микросервисом crm_analyzer_service...
      </div>
    );
  }

  const cardStyle = {
    flex: 1,
    minWidth: '140px',
    background: '#1a1a1a',
    border: '1px solid #333',
    padding: '15px 20px',
    borderRadius: '6px',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px'
  };

  return (
    <div style={{ display: 'flex', gap: '15px', marginBottom: '25px', flexWrap: 'wrap' }}>
      
      <div style={cardStyle}>
        <span style={{ fontSize: '11px', color: '#aaa', fontWeight: 'bold', textTransform: 'uppercase' }}>💰 Общая выручка сети</span>
        <span style={{ fontSize: '22px', fontWeight: 'bold', color: '#2ea44f' }}>
          {metrics.total_sales.toLocaleString('ru-RU')} ₽
        </span>
        <span style={{ fontSize: '10px', color: '#555' }}>Чистый накопительный итог</span>
      </div>

      <div style={cardStyle}>
        <span style={{ fontSize: '11px', color: '#aaa', fontWeight: 'bold', textTransform: 'uppercase' }}>👥 Активные клиенты</span>
        <span style={{ fontSize: '22px', fontWeight: 'bold', color: '#4fa8ff' }}>
          {metrics.active_customers} чеков
        </span>
        <span style={{ fontSize: '10px', color: '#555' }}>Уникальные розничные продажи</span>
      </div>

      <div style={cardStyle}>
        <span style={{ fontSize: '11px', color: '#aaa', fontWeight: 'bold', textTransform: 'uppercase' }}>📈 Конверсия кассы</span>
        <span style={{ fontSize: '22px', fontWeight: 'bold', color: '#ffb74d' }}>
          {metrics.conversion_rate}
        </span>
        <span style={{ fontSize: '10px', color: '#555' }}>Эффективность открытых смен</span>
      </div>

    </div>
  );
};
