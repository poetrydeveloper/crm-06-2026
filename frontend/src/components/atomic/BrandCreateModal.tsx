// frontend/src/components/atomic/BrandCreateModal.tsx
import React, { useState } from 'react';

interface BrandCreateModalProps {
  onClose: () => void;
  onBrandCreated: (brandId: number, brandName: string) => void;
}

export const BrandCreateModal: React.FC<BrandCreateModalProps> = ({ onClose, onBrandCreated }) => {
  const [brandName, setBrandName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = brandName.trim();
    if (!name) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/catalog/brands', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });

      const data = await response.json();

      if (response.ok) {
        onBrandCreated(data.brand_id, data.name || name);
        setBrandName('');
        onClose();
      } else {
        setError(data.detail || 'Ошибка при создании бренда');
      }
    } catch (err) {
      setError('Ошибка сети');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{ width: '400px', zIndex: 1101 }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="card-title mb-3">Новый бренд</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Название бренда</label>
            <input
              type="text"
              className="form-control"
              placeholder="Например: Toptul"
              value={brandName}
              onChange={(e) => setBrandName(e.target.value)}
              autoFocus
            />
          </div>

          {error && (
            <div className="alert alert-danger" style={{ padding: '8px 12px', marginBottom: '12px' }}>
              {error}
            </div>
          )}

          <div className="d-flex gap-8">
            <button type="submit" className="btn btn-success btn-sm" disabled={loading}>
              {loading ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button type="button" className="btn btn-outline btn-sm" onClick={onClose}>
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};