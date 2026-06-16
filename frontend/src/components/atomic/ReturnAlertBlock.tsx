// frontend/src/components/atomic/ReturnAlertBlock.tsx
import React from 'react';

interface RelationData {
  has_parent_relation: boolean;
  parent_unit_id?: number;
  parent_serial_number?: string;
  message: string;
}

interface ReturnAlertBlockProps {
  relation: RelationData | null;
  onNavigateToAssembly: () => void;
}

export const ReturnAlertBlock: React.FC<ReturnAlertBlockProps> = ({ relation, onNavigateToAssembly }) => {
  if (!relation) return null;

  return (
    <div style={{ 
      background: relation.has_parent_relation ? '#2c1a04' : '#141e17', 
      border: relation.has_parent_relation ? '1px solid #e65100' : '1px solid #2ea44f', 
      padding: '15px 20px', 
      borderRadius: '6px', 
      marginBottom: '25px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <span style={{ 
          fontWeight: 'bold', 
          color: relation.has_parent_relation ? '#ffb74d' : '#a5d6a7',
          fontSize: '14px'
        }}>
          {relation.has_parent_relation ? '⚠️ ОБНАРУЖЕН РАЗДЕРБАНЕННЫЙ НАБОР' : '✔️ ЧИСТАЯ РОЗНИЧНАЯ ЕДИНИЦА'}
        </span>
        <p style={{ margin: 0, fontSize: '13px', color: '#ddd' }}>{relation.message}</p>
      </div>

      {relation.has_parent_relation && (
        <button
          type="button"
          onClick={onNavigateToAssembly}
          style={{ 
            background: 'transparent', 
            color: '#4fa8ff', 
            border: '1px solid #4fa8ff', 
            padding: '6px 14px', 
            borderRadius: '4px', 
            cursor: 'pointer', 
            fontWeight: 'bold',
            fontSize: '12px',
            transition: 'all 0.2s'
          }}
        >
          ⚙️ Перейти к сборке наборов
        </button>
      )}
    </div>
  );
};
