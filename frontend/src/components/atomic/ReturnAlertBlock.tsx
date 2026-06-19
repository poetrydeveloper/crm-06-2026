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
    <div className={`alert ${relation.has_parent_relation ? 'alert-warning' : 'alert-success'} mb-3`}>
      <div className="d-flex justify-between align-center">
        <div>
          <strong>{relation.has_parent_relation ? '⚠️ Разобранный набор' : '✔️ Независимая единица'}</strong>
          <p style={{ margin: '4px 0 0 0', fontSize: '13px' }}>{relation.message}</p>
        </div>
        {relation.has_parent_relation && (
          <button className="btn btn-sm btn-outline" onClick={onNavigateToAssembly}>
            К сборке
          </button>
        )}
      </div>
    </div>
  );
};