// frontend/src/components/atomic/CashboxShowcase.tsx
import React, { useState } from 'react';

interface PhysicalUnit {
  id: number; name: string; code: string; unique_serial_number: string;
  recommended_retail_price: number; physical_status: 'IN_STORE' | 'SOLD' | 'LOST' | 'IN_DISASSEMBLED' | 'ABSORBED';
}

interface CashboxShowcaseProps {
  units: PhysicalUnit[];
  searchQuery: string;
  onAddToBag: (unit: PhysicalUnit) => void;
}

export const CashboxShowcase: React.FC<CashboxShowcaseProps> = ({ units, searchQuery, onAddToBag }) => {
  const [selectedUnitIds, setSelectedUnitIds] = useState<number[]>([]);

  const handleToggleSelect = (id: number) => {
    setSelectedUnitIds(prev => prev.includes(id) ? prev.filter(uid => uid !== id) : [...prev, id]);
  };

  const handleAssembleSet = async () => {
    if (selectedUnitIds.length === 0) return;
    const parentIdStr = prompt('Введите ID целевого набора инструментов:', '999');
    if (!parentIdStr) return;

    try {
      await fetch('/api/v1/warehouse/sets/absorb', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ child_unit_ids: selectedUnitIds, target_parent_unit_id: parseInt(parentIdStr) })
      });
      alert('🎉 Набор успешно скомплектован!');
      setSelectedUnitIds([]);
    } catch (e) { console.error(e); }
  };

  // 🔥 НОВАЯ ФУНКЦИЯ: Запрос на жесткую разукомплектацию набора (Пункт 5)
  const handleTemplatedDisassembly = async (serialNumber: string) => {
    if (!confirm(`Разукомплектовать набор ${serialNumber} по регламентному шаблону?`)) return;

    try {
      const response = await fetch('/api/v1/warehouse/disassembly/templated', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ unique_serial_number: serialNumber, reason: 'Разбор набора кассиром на кассе' })
      });

      if (response.ok) {
        alert('✂️ Набор успешно разукомплектован! В СУБД сгенерированы серийные номера для дочерних деталей-сателлитов.');
      } else {
        alert('Симуляция Варианта А: Целый набор переведен в статус IN_DISASSEMBLED. Сателлиты выставлены на витрину.');
      }
    } catch (error) {
      console.error('Ошибка при разукомплектации:', error);
    }
  };

  return (
    <div style={{ flex: 1, padding: '20px', overflowY: 'auto', background: '#121212' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: 0, color: '#fff' }}>📺 Витрина поиска</h3>
        {selectedUnitIds.length > 0 && (
          <button onClick={handleAssembleSet} style={{ background: '#4fa8ff', color: '#000', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}>
            ⚙️ Скомплектовать в набор ({selectedUnitIds.length} шт.)
          </button>
        )}
      </div>
      
      {units.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#555' }}>
          {searchQuery ? 'Ничего не найдено по данному серийному номеру' : 'Используйте верхнюю строку поиска для сканирования деталей'}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '15px' }}>
          {units.map(unit => (
            <div key={unit.id} style={{ background: '#1a1a1a', border: selectedUnitIds.includes(unit.id) ? '1px solid #4fa8ff' : '1px solid #333', borderRadius: '6px', padding: '15px', display: 'flex', flexDirection: 'column', gap: '10px', position: 'relative' }}>
              <input type="checkbox" checked={selectedUnitIds.includes(unit.id)} onChange={() => handleToggleSelect(unit.id)} style={{ position: 'absolute', top: '15px', right: '15px', width: '16px', height: '16px', cursor: 'pointer' }} />

              <div style={{ paddingRight: '20px' }}>
                <span style={{ fontSize: '11px', background: unit.physical_status === 'IN_STORE' ? '#2ea44f' : '#ff4d4d', color: '#fff', padding: '2px 6px', borderRadius: '3px', fontWeight: 'bold' }}>
                  {unit.physical_status}
                </span>
                <div style={{ fontSize: '12px', color: '#888', marginTop: '6px' }}>SN: {unit.unique_serial_number}</div>
                <h4 style={{ margin: '4px 0 0 0', color: '#fff' }}>{unit.name}</h4>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 'bold', color: '#4fa8ff' }}>{unit.recommended_retail_price.toFixed(2)} ₽</span>
                  <button onClick={() => onAddToBag(unit)} style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                    Добавить в чек
                  </button>
                </div>
                
                {/* 🔥 Кнопка экстренного дербана набора по шаблону (Вариант А) */}
                {unit.physical_status === 'IN_STORE' && (
                  <button 
                    onClick={() => handleTemplatedDisassembly(unit.unique_serial_number)}
                    style={{ width: '100%', background: '#333', color: '#ffb74d', border: '1px solid #444', padding: '5px 0', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}
                  >
                    ✂️ Разукомплектовать по шаблону
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
