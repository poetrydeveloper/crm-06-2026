// frontend/src/components/atomic/DisassemblyModal.tsx
import React, { useState, useEffect } from 'react';
import { DisassemblyMenu } from './DisassemblyMenu';
import { TemplateConstructor } from './TemplateConstructor';

interface DisassemblyModalProps {
  unitSerial: string;
  productId: number;
  onClose: () => void;
  onSuccess: () => void;
}

export const DisassemblyModal: React.FC<DisassemblyModalProps> = ({ unitSerial, productId, onClose, onSuccess }) => {
  const [mode, setMode] = useState<'loading' | 'select' | 'create_template' | 'quick_freeze'>('loading');
  const [hasTemplate, setHasTemplate] = useState<boolean | null>(null);
  const [productName, setProductName] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const prodRes = await fetch('/api/v1/catalog/products/all');
        if (prodRes.ok) {
          const prod = (await prodRes.json()).find((p: any) => p.id === productId);
          if (prod) setProductName(prod.name.replace(/_/g, ' '));
        }
        const tmplRes = await fetch(`/api/v1/warehouse/disassembly/check-template?product_id=${productId}`);
        setHasTemplate(tmplRes.ok ? (await tmplRes.json()).has_template : false);
      } catch { setHasTemplate(false); }
      setMode('select');
    })();
  }, [productId]);

  const handleApplyTemplate = async () => {
    const r = await fetch('/api/v1/warehouse/disassembly/templated', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ unique_serial_number: unitSerial }),
    });
    if (r.ok) { alert('Набор разобран. Сателлиты созданы.'); onSuccess(); onClose(); }
    else alert((await r.json()).detail || 'Ошибка');
  };

  const overlay: React.CSSProperties = {
    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
    background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1100,
  };

  if (mode === 'loading') return <div style={overlay} onClick={onClose}><div className="card" style={{padding:30}} onClick={e=>e.stopPropagation()}>Загрузка...</div></div>;

  if (mode === 'create_template') return (
    <TemplateConstructor
      productId={productId} productName={productName} unitSerial={unitSerial}
      onBack={() => setMode('select')}
      onSaved={() => { setHasTemplate(true); setMode('select'); }}
      onClose={onClose}
    />
  );

  return (
    <DisassemblyMenu
      productName={productName} unitSerial={unitSerial} hasTemplate={hasTemplate}
      onApplyTemplate={handleApplyTemplate}
      onCreateTemplate={() => setMode('create_template')}
      onPartial={() => setMode('quick_freeze')}
      onClose={onClose}
    />
  );
};