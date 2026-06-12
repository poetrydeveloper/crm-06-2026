// frontend/src/components/atomic/ProductGrid.tsx
import React from 'react';
import { ProductCard } from './ProductCard';

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
}

interface ProductGridProps {
  products: Product[];
  onCreateProduct: () => void;
  onEditProduct: (id: number) => void;
  onDeleteProduct: (id: number) => void;
}

export const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  onCreateProduct,
  onEditProduct,
  onDeleteProduct,
}) => {
  return (
    <div style={{ flex: 1, padding: '20px', background: '#121212' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, color: '#fff' }}>📦 Номенклатурные карточки</h3>
        <button onClick={onCreateProduct} style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>
          + Создать товар
        </button>
      </div>

      {products.length === 0 ? (
        <div style={{ color: '#666', textAlign: 'center', padding: '4px' }}>В выбранной категории пока нет товаров.</div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: '20px'
        }}>
          {products.map(prod => (
            <ProductCard
              key={prod.id}
              id={prod.id}
              name={prod.name}
              code={prod.code}
              price={prod.recommended_retail_price}
              onEdit={onEditProduct}
              onDelete={onDeleteProduct}
            />
          ))}
        </div>
      )}
    </div>
  );
};
