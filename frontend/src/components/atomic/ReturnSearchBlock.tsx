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
  isLoading,
}) => {
  return (
    <form onSubmit={onCheckRelation} className="card mb-3">
      <div className="d-flex gap-12 align-center">
        <div style={{ flex: 1 }}>
          <label className="form-label">Серийный номер (SN)</label>
          <input
            type="text"
            className="form-control"
            required
            value={serialNumber}
            onChange={(e) => onSerialChange(e.target.value)}
            placeholder="SN-DERBAN-A1B2C3"
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={isLoading} style={{ alignSelf: 'flex-end' }}>
          {isLoading ? 'Проверка...' : 'Проверить'}
        </button>
      </div>
    </form>
  );
};