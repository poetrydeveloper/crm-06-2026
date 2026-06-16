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

  // 🔍 1. Предварительный аудит связей детали перед возвратом
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
        setRelation({ has_parent_relation: false, message: 'Ошибка связи с СУБД при аудите серийного номера' });
      }
    } catch (error) {
      console.error('Ошибка проверки связей:', error);
      setRelation({ has_parent_relation: false, message: 'Сетевой сбой кассового узла' });
    } finally {
      setLoading(false);
    }
  };

  // 🔄 2. Проведение транзакции возврата (POST /api/v1/cash/returns)
  const handleExecuteReturn = async () => {
    if (!serialNumber.trim()) return;

    try {
      const response = await fetch('/api/v1/cash/returns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          unique_serial_number: serialNumber.trim(),
          return_reason: returnReason
        })
      });

      if (response.ok) {
        alert('🎉 Товар успешно принят обратно на баланс! Юнит переведен в статус IN_STORE и выставлен на кассу.');
        setSerialNumber('');
        setRelation(null);
      } else {
        const errData = await response.json();
        alert(`Ошибка проведения возврата: ${errData.detail || 'Сбой СУБД'}`);
      }
    } catch (error) {
      console.error('Ошибка сети при возврате:', error);
    }
  };

  // ⚙️ 3. SPA-переход на экран комплектации наборов, если обнаружен LOST-родитель
  const handleNavigateToAssembly = () => {
    window.history.pushState({}, '', '/warehouse');
    window.dispatchEvent(new Event('popstate'));
  };

  return (
    <div style={{ padding: '20px', background: '#121212', color: '#fff', minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#4fa8ff' }}>🔄 Оформление возвратов от покупателей (Команда 0403)</h2>
        <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#666' }}>Интеллектуальный контроль комплектности и автоматический аудит раздербаненных наборов</p>
      </div>

      {/* Атомный блок сканирования/поиска */}
      <ReturnSearchBlock 
        serialNumber={serialNumber} 
        onSerialChange={setSerialNumber} 
        onCheckRelation={handleCheckRelation} 
        isLoading={loading} 
      />

      {/* Атомный умный индификатор связей */}
      <ReturnAlertBlock 
        relation={relation} 
        onNavigateToAssembly={handleNavigateToAssembly} 
      />

      {/* Блок подтверждения и проведения возврата (рендерится только если товар найден) */}
      {relation && (
        <div style={{ background: '#1a1a1a', padding: '20px', borderRadius: '6px', border: '1px solid #333' }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#fff' }}>📝 Подтверждение кассовой операции</h3>
          
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>Укажите причину возврата товара:</label>
            <input 
              type="text" 
              value={returnReason} 
              onChange={(e) => setReturnReason(e.target.value)} 
              style={{ width: '100%', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} 
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              onClick={() => { setSerialNumber(''); setRelation(null); }} 
              style={{ flex: 1, padding: '10px', background: '#333', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Отмена
            </button>
            <button 
              onClick={handleExecuteReturn} 
              style={{ flex: 1, padding: '10px', background: '#e65100', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              🔄 Пробить чек возврата
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
