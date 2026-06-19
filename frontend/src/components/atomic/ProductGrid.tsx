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
  onCreateProduct: () => void; // Сохранено для обратной совместимости пропсов
  onEditProduct: (id: number) => void;
  onDeleteProduct: (id: number) => void;
}

export const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  onEditProduct,
  onDeleteProduct,
}) => {
  return (
    <div style={{ flex: 1, padding: '20px', background: '#121212', overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #333', paddingBottom: '10px' }}>
        <h3 style={{ margin: 0, color: '#fff', fontSize: '16px' }}>📦 Номенклатурные карточки товаров</h3>
      </div>

      {products.length === 0 ? (
        <div style={{ color: '#666', textAlign: 'center', padding: '40px 0' }}>
          В выбранной категории пока нет товаров или ничего не найдено умным поиском.
        </div>
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
