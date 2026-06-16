// frontend/src/components/atomic/ReturnSearchBlock.tsx
import React from 'react';

interface ReturnSearchBlockProps {
  serialNumber: string;
  onSerialChange: (value: string) => void;
  onCheckRelation: (e: React.FormEvent) => void;
  isLoading: boolean;
}

export const ReturnSearchBlock: React.FC<ReturnSearchBlockProps> = ({
  serialNumber,
  onSerialChange,
  onCheckRelation,
  isLoading
}) => {
  return (
    <form onSubmit={onCheckRelation} style={{ 
      background: '#1a1a1a', 
      padding: '20px', 
      borderRadius: '6px', 
      border: '1px solid #333',
      marginBottom: '20px',
      display: 'flex',
      gap: '15px',
      alignItems: 'flex-end'
    }}>
      <div style={{ flex: 1 }}>
        <label style={{ display: 'block', fontSize: '13px', color: '#aaa', marginBottom: '8px', fontWeight: 'bold' }}>
          🔌 Сканирование или ввод серийного номера (SN):
        </label>
        <input
          type="text"
          required
          value={serialNumber}
          onChange={(e) => onSerialChange(e.target.value)}
          placeholder="например, SN-DERBAN-A1B2C3"
          style={{ 
            width: '100%', 
            padding: '10px', 
            background: '#2d2d2d', 
            color: '#fff', 
            border: '1px solid #444', 
            borderRadius: '4px',
            fontSize: '15px',
            outline: 'none'
          }}
        />
      </div>
      
      <button
        type="submit"
        disabled={isLoading}
        style={{ 
          background: '#4fa8ff', 
          color: '#000', 
          border: 'none', 
          padding: '11px 24px', 
          borderRadius: '4px', 
          cursor: isLoading ? 'not-allowed' : 'pointer', 
          fontWeight: 'bold',
          fontSize: '14px',
          transition: 'background 0.2s'
        }}
      >
        {isLoading ? 'Проверка...' : '🔍 Проверить связи юнита'}
      </button>
    </form>
  );
};
