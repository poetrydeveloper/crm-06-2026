// frontend/src/components/atomic/CashDaysControls.tsx
import React from 'react';

interface CashDaysControlsProps {
  onOpenDay: () => void;
  onCloseDay: () => void;
  onEmergencyReopen: () => void;
}

export const CashDaysControls: React.FC<CashDaysControlsProps> = ({
  onOpenDay,
  onCloseDay,
  onEmergencyReopen,
}) => {
  return (
    <div className="card mb-3">
      <div className="d-flex gap-12">
        <button className="btn btn-success" onClick={onOpenDay}>
          Открыть смену
        </button>
        <button className="btn btn-danger" onClick={onCloseDay}>
          Закрыть смену
        </button>
        <button className="btn btn-warning" onClick={onEmergencyReopen} style={{ marginLeft: 'auto' }}>
          Экстренное переоткрытие
        </button>
      </div>
    </div>
  );
};