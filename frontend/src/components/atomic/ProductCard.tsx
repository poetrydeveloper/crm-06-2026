// frontend/src/components/atomic/ProductCard.tsx
import React from 'react';

interface ProductCardProps {
  id: number;
  name: string;
  code: string;
  price: number;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  id,
  name,
  code,
  price,
  onEdit,
  onDelete,
}) => {
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
        <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Арт: {code}</div>
        <h4 style={{ margin: 0, fontSize: '16px', color: '#fff', lineHeight: '1.4' }}>{name}</h4>
      </div>
      
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '10px'
      }}>
        <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#2ea44f' }}>
          {price.toFixed(2)} ₽
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={() => onEdit(id)} style={{ background: '#333', border: 'none', padding: '6px 10px', borderRadius: '4px', color: '#fff', cursor: 'pointer' }}>
            ✏️
          </button>
          <button onClick={() => onDelete(id)} style={{ background: '#333', border: 'none', padding: '6px 10px', borderRadius: '4px', color: '#ff4d4d', cursor: 'pointer' }}>
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
};