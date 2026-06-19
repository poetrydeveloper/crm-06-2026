// frontend/src/components/atomic/ProductCard.tsx
import React from 'react';

interface ProductCardProps {
  id: number;
  name: string;
  code: string;
  price: number;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
  // Опциональный массив картинок (поддерживаем ТЗ Истории 3)
  images?: string[]; 
}

export const ProductCard: React.FC<ProductCardProps> = ({
  id,
  name,
  code,
  price,
  onEdit,
  onDelete,
  images
}) => {
  // Если картинок нет, используем эталонный системный плейсхолдер
  const coverImage = images && images.length > 0 ? images[0] : "/assets/hero.png";

  return (
    <div style={{
      background: '#1a1a1a',
      border: '1px solid #333',
      borderRadius: '8px',
      padding: '15px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      gap: '10px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
    }}>
      <div>
        {/* Визуальный блок обложки карточки товара */}
        <div style={{ width: '100%', height: '120px', background: '#2d2d2d', borderRadius: '4px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
          <span style={{ fontSize: '24px' }}>🛠️</span>
        </div>

        <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Арт: {code}</div>
        
        {/* 🔥 ИСПРАВЛЕНО: textTransform автоматически делает первую букву заглавной в браузере */}
        <h4 style={{ margin: 0, fontSize: '15px', color: '#fff', lineHeight: '1.4', textTransform: 'capitalize' }}>
          {name.replace(/_/g, ' ')}
        </h4>
      </div>
      
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '10px'
      }}>
        <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#ffb74d' }}>
          {price.toFixed(2)} ₽
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={() => onEdit(id)} style={{ background: '#2d2d2d', border: '1px solid #444', padding: '6px 10px', borderRadius: '4px', color: '#fff', cursor: 'pointer' }}>
            ✏️
          </button>
          <button onClick={() => onDelete(id)} style={{ background: '#2d2d2d', border: '1px solid #444', padding: '6px 10px', borderRadius: '4px', color: '#ff4d4d', cursor: 'pointer' }}>
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
};
