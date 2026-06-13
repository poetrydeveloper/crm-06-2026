// frontend/src/components/atomic/CashboxStatus.tsx
import React from 'react';

interface CashboxStatusProps {
  status: 'ЗАКРЫТА' | 'ОТКРЫТА';
}

export const CashboxStatus: React.FC<CashboxStatusProps> = ({ status }) => {
  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      gap: '12px', 
      background: '#222', 
      padding: '6px 15px', 
      borderRadius: '6px', 
      border: '1px solid #333' 
    }}>
      <span style={{ fontSize: '14px', color: '#aaa' }}>Кассовая смена:</span>
      <span style={{ 
        fontWeight: 'bold', 
        fontSize: '14px', 
        color: status === 'ОТКРЫТА' ? '#2ea44f' : '#ff4d4d' 
      }}>
        ● {status}
      </span>
    </div>
  );
};
