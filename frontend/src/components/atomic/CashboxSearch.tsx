// frontend/src/components/atomic/CashboxSearch.tsx
import React from 'react';

interface CashboxSearchProps {
  value: string;
  onChange: (text: string) => void;
}

export const CashboxSearch: React.FC<CashboxSearchProps> = ({ value, onChange }) => {
  return (
    <input
      type="text"
      placeholder="🔍 Введите или сосканируйте уникальный серийный номер (SN)..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        width: '100%',
        maxWidth: '500px',
        padding: '8px 12px',
        borderRadius: '4px',
        border: '1px solid #444',
        background: '#2d2d2d',
        color: '#fff',
        outline: 'none'
      }}
    />
  );
};
