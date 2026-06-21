// frontend/src/components/atomic/DisassemblyMenu.tsx
import React from 'react';

interface DisassemblyMenuProps {
  productName: string;
  unitSerial: string;
  hasTemplate: boolean | null;
  onApplyTemplate: () => void;
  onCreateTemplate: () => void;
  onPartial: () => void;
  onClose: () => void;
}

export const DisassemblyMenu: React.FC<DisassemblyMenuProps> = ({
  productName, unitSerial, hasTemplate, onApplyTemplate, onCreateTemplate, onPartial, onClose,
}) => (
  <div style={overlay} onClick={onClose}>
    <div className="card" style={{ padding: '24px', width: '400px', zIndex: 1101 }} onClick={e => e.stopPropagation()}>
      <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 700 }}>Разукомплектация</h3>
      <div className="text-muted" style={{ fontSize: '13px', marginBottom: '16px' }}>
        <strong>{productName}</strong><br/>SN: {unitSerial}
      </div>

      <button className="btn btn-success mb-2" style={{ width: '100%', display: 'block' }} onClick={onApplyTemplate} disabled={!hasTemplate}>
        Вариант А: Разобрать по шаблону {!hasTemplate && '(нет шаблона)'}
      </button>
      <button className="btn btn-outline mb-2" style={{ width: '100%', display: 'block' }} onClick={onCreateTemplate}>
        {hasTemplate ? 'Изменить шаблон' : 'Создать шаблон'}
      </button>
      <button className="btn btn-warning mb-2" style={{ width: '100%', display: 'block' }} onClick={onPartial}>
        Вариант В: Частичный разбор
      </button>
      <button className="btn btn-outline" style={{ width: '100%', display: 'block', marginTop: '8px' }} onClick={onClose}>
        Закрыть
      </button>
    </div>
  </div>
);

const overlay: React.CSSProperties = {
  position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
  background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1100,
};