// frontend/src/components/atomic/AnalyticsFallbackPlaceholder.tsx
import React from 'react';

export const AnalyticsFallbackPlaceholder: React.FC = () => {
  return (
    <div style={{
      background: '#2c1515',
      border: '1px solid #ff4d4d',
      padding: '24px',
      borderRadius: '8px',
      textAlign: 'center',
      marginTop: '15px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
    }}>
      <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚠️</div>
      <h3 style={{ margin: '0 0 8px 0', color: '#ff6b6b', fontSize: '16px', fontWeight: 'bold' }}>
        Режим ограниченной функциональности снабжения
      </h3>
      <p style={{ margin: '0 0 15px 0', fontSize: '13px', color: '#ddd', lineHeight: '1.5' }}>
        Выделенный микросервис аналитики дефицита остатков (<code style={{ color: '#ffb74d', fontFamily: 'monospace' }}>crm_analyzer_service</code>) временно недоступен по сети. 
        Автоматический расчёт рисков приостановлен.
      </p>
      <div style={{ fontSize: '11px', color: '#888', fontStyle: 'italic' }}>
        Система автоматически восстановит штатный режим, как только фоновый контейнер завершит перезапуск.
      </div>
    </div>
  );
};
