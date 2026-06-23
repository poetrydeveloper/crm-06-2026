// frontend/src/components/atomic/ReturnModal.tsx
import React, { useState, useEffect } from 'react';

interface SoldUnit {
  unit_id: number;
  unique_serial_number: string;
  product_name: string;
  product_code: string;
  sold_price: number;
  sold_at: string;
  event_id: number;
}

interface ReturnModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

const DAY_OPTIONS = [
  { label: '5 дней', value: 5 },
  { label: '10 дней', value: 10 },
  { label: '30 дней', value: 30 },
  { label: 'Все', value: 365 },
];

export const ReturnModal: React.FC<ReturnModalProps> = ({ onClose, onSuccess }) => {
  const [days, setDays] = useState(5);
  const [units, setUnits] = useState<SoldUnit[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUnit, setSelectedUnit] = useState<SoldUnit | null>(null);
  const [action, setAction] = useState<'return' | 'change_price'>('return');
  const [newPrice, setNewPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadUnits = async () => {
    setLoading(true);
    try {
      const r = await fetch(`/api/v1/cash/days/current/units?days=${days}`);
      if (r.ok) {
        const data = await r.json();
        setUnits(data.units || []);
      }
    } catch {}
    setLoading(false);
  };

  useEffect(() => { loadUnits(); }, [days]);

  const filteredUnits = searchQuery
    ? units.filter((u) =>
        u.unique_serial_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.product_code.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : units;

  const handleSubmit = async () => {
    if (!selectedUnit) return;
    setError(null);

    if (action === 'change_price') {
      const price = parseFloat(newPrice.replace(',', '.'));
      if (isNaN(price) || price <= 0) {
        setError('Введите корректную цену');
        return;
      }
    }

    try {
      const body: any = {
        unit_id: selectedUnit.unit_id,
        action: action,
      };
      if (action === 'change_price') {
        body.new_price = parseFloat(newPrice.replace(',', '.'));
      }

      const r = await fetch('/api/v1/cash/sales/adjust', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (r.ok) {
        alert(action === 'return' ? 'Юнит возвращён' : 'Цена изменена');
        onSuccess();
        onClose();
      } else {
        const err = await r.json();
        setError(err.detail || 'Ошибка');
      }
    } catch {}
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1100 }} onClick={onClose}>
      <div className="card" style={{ width: '560px', maxWidth: '95vw', maxHeight: '90vh', overflowY: 'auto', padding: '24px' }} onClick={(e) => e.stopPropagation()}>
        <h3 className="card-title">Возврат / Изменение цены</h3>

        {/* Фильтр по дням */}
        <div className="d-flex gap-8 mb-3">
          {DAY_OPTIONS.map((opt) => (
            <button key={opt.value} className={`btn btn-sm ${days === opt.value ? 'btn-primary' : 'btn-outline'}`} onClick={() => setDays(opt.value)}>
              {opt.label}
            </button>
          ))}
        </div>

        {/* Поиск */}
        <input
          type="text"
          className="form-control mb-3"
          placeholder="Поиск по серийному номеру или названию..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        {/* Список юнитов */}
        {loading ? (
          <div className="text-muted text-center" style={{ padding: '20px' }}>Загрузка...</div>
        ) : filteredUnits.length === 0 ? (
          <div className="text-muted text-center" style={{ padding: '20px' }}>Нет проданных юнитов</div>
        ) : (
          <div style={{ maxHeight: '250px', overflowY: 'auto', marginBottom: '16px', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)' }}>
            {filteredUnits.map((u) => (
              <label
                key={u.event_id}
                className="d-flex align-center gap-8"
                style={{
                  padding: '10px 12px',
                  cursor: 'pointer',
                  borderBottom: '1px solid var(--border)',
                  background: selectedUnit?.event_id === u.event_id ? 'var(--bg-secondary)' : undefined,
                }}
              >
                <input
                  type="radio"
                  name="soldUnit"
                  checked={selectedUnit?.event_id === u.event_id}
                  onChange={() => {
                    setSelectedUnit(u);
                    setNewPrice(String(u.sold_price));
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500, textTransform: 'capitalize' }}>{u.product_name.replace(/_/g, ' ')}</div>
                  <div className="text-muted text-mono" style={{ fontSize: '12px' }}>
                    {u.unique_serial_number} — продано за {u.sold_price.toFixed(2)} ₽
                  </div>
                  <div className="text-muted" style={{ fontSize: '11px' }}>{new Date(u.sold_at).toLocaleString('ru-RU')}</div>
                </div>
              </label>
            ))}
          </div>
        )}

        {/* Действия после выбора */}
        {selectedUnit && (
          <div className="mb-3">
            <div className="form-group">
              <label className="form-label">Действие</label>
              <select className="form-control" value={action} onChange={(e) => setAction(e.target.value as any)}>
                <option value="return">Возврат (юнит вернётся на полку)</option>
                <option value="change_price">Изменение цены</option>
              </select>
            </div>

            {action === 'change_price' && (
              <div className="form-group mt-2">
                <label className="form-label">
                  Новая цена (было: {selectedUnit.sold_price.toFixed(2)} ₽)
                </label>
                <input
                  type="text"
                  inputMode="decimal"
                  className="form-control"
                  value={newPrice}
                  onFocus={(e) => e.target.select()}
                  onChange={(e) => setNewPrice(e.target.value.replace(',', '.'))}
                  style={{ width: '150px' }}
                />
              </div>
            )}

            {action === 'return' && (
              <div className="alert alert-warning mt-2" style={{ padding: '10px 14px', fontSize: '13px' }}>
                Будет создано событие RETURN на сумму <strong>−{selectedUnit.sold_price.toFixed(2)} ₽</strong>. Юнит вернётся в статус IN_STORE.
              </div>
            )}
          </div>
        )}

        {error && <div className="alert alert-danger" style={{ padding: '8px 12px' }}>{error}</div>}

        <div className="d-flex gap-8">
          <button className="btn btn-outline" onClick={onClose}>Отмена</button>
          <button className="btn btn-success" disabled={!selectedUnit} onClick={handleSubmit}>
            {action === 'return' ? 'Оформить возврат' : 'Изменить цену'}
          </button>
        </div>
      </div>
    </div>
  );
};