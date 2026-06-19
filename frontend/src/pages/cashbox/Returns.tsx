// frontend/src/pages/cashbox/Returns.tsx
import React, { useState } from 'react';
import { ReturnSearchBlock } from '../../components/atomic/ReturnSearchBlock';
import { ReturnAlertBlock } from '../../components/atomic/ReturnAlertBlock';

interface RelationData {
  has_parent_relation: boolean;
  parent_unit_id?: number;
  parent_serial_number?: string;
  message: string;
}

export const Returns: React.FC = () => {
  const [serialNumber, setSerialNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [relation, setRelation] = useState<RelationData | null>(null);
  const [returnReason, setReturnReason] = useState('Возврат от покупателя');

  const handleCheckRelation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!serialNumber.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/v1/cash/returns/check-relation?sn=${encodeURIComponent(serialNumber.trim())}`);
      if (response.ok) {
        const data = await response.json();
        setRelation(data);
      } else {
        setRelation({ has_parent_relation: false, message: 'Ошибка проверки серийного номера' });
      }
    } catch (error) {
      console.error(error);
      setRelation({ has_parent_relation: false, message: 'Сетевой сбой' });
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteReturn = async () => {
    if (!serialNumber.trim()) return;

    try {
      const response = await fetch('/api/v1/cash/returns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          unique_serial_number: serialNumber.trim(),
          return_reason: returnReason,
        }),
      });

      if (response.ok) {
        alert('Товар возвращён на баланс. Статус: IN_STORE');
        setSerialNumber('');
        setRelation(null);
      } else {
        const errData = await response.json();
        alert(`Ошибка: ${errData.detail || 'Сбой'}`);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleNavigateToAssembly = () => {
    window.history.pushState({}, '', '/warehouse');
    window.dispatchEvent(new Event('popstate'));
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <div>
          <h2 className="page-title">Оформление возвратов</h2>
          <p className="text-muted" style={{ marginTop: '4px' }}>Контроль комплектности и аудит наборов</p>
        </div>
      </div>

      <ReturnSearchBlock
        serialNumber={serialNumber}
        onSerialChange={setSerialNumber}
        onCheckRelation={handleCheckRelation}
        isLoading={loading}
      />

      <ReturnAlertBlock relation={relation} onNavigateToAssembly={handleNavigateToAssembly} />

      {relation && (
        <div className="card">
          <h3 className="card-title">Подтверждение операции</h3>

          <div className="form-group">
            <label className="form-label">Причина возврата</label>
            <input
              type="text"
              className="form-control"
              value={returnReason}
              onChange={(e) => setReturnReason(e.target.value)}
            />
          </div>

          <div className="d-flex gap-8">
            <button className="btn btn-outline" onClick={() => { setSerialNumber(''); setRelation(null); }}>
              Отмена
            </button>
            <button className="btn btn-warning" onClick={handleExecuteReturn}>
              Провести возврат
            </button>
          </div>
        </div>
      )}
    </div>
  );
};