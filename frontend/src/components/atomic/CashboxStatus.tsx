// frontend/src/components/atomic/CashboxStatus.tsx
import React from 'react';

interface CashboxStatusProps {
  status: 'ЗАКРЫТА' | 'ОТКРЫТА';
}

export const CashboxStatus: React.FC<CashboxStatusProps> = ({ status }) => {
  const isOpen = status === 'ОТКРЫТА';

  return (
    <div className="d-flex align-center gap-8">
      <span className="text-muted" style={{ fontSize: '13px' }}>Смена:</span>
      <span className={`badge ${isOpen ? 'badge-success' : 'badge-danger'}`}>
        {status}
      </span>
    </div>
  );
};