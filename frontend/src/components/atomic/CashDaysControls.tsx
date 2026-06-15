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
  onEmergencyReopen
}) => {
  return (
    <div style={{ 
      display: 'flex', 
      gap: '12px', 
      background: '#1a1a1a', 
      padding: '15px', 
      borderRadius: '6px', 
      border: '1px solid #333',
      marginBottom: '20px'
    }}>
      <button
        onClick={onOpenDay}
        style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '10px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
      >
        🔓 Открыть день
      </button>
      
      <button
        onClick={onCloseDay}
        style={{ background: '#ff4d4d', color: '#fff', border: 'none', padding: '10px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
      >
        🔒 Закрыть день
      </button>

      <button
        onClick={onEmergencyReopen}
        style={{ background: '#333', color: '#ffb74d', border: '1px solid #444', padding: '10px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', marginLeft: 'auto' }}
      >
        ⚡ Экстренно переоткрыть смену
      </button>
    </div>
  );
};
