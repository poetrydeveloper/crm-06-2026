// frontend/src/components/atomic/UnitMapCard.tsx
import React from 'react';

interface ProductWithStock {
  id: number;
  name: string;
  code: string;
  brand_name: string;
  in_stock: number;
  expected_qty: number;
  disassembled_qty: number;
}

export const UnitMapCard: React.FC<{ product: ProductWithStock }> = ({ product }) => (
  <div className="unitmap-card">
    <div className="unitmap-header">
      <div className="unitmap-code">{product.code}</div>
      {product.brand_name && <div className="unitmap-brand">{product.brand_name}</div>}
      <div className="unitmap-name">{product.name.replace(/_/g, ' ')}</div>
    </div>
    <div className="unitmap-circle-wrap">
      <div className="unitmap-circle">
        {product.expected_qty > 0 && (
          <div className="circle-part circle-top">
            <span className="circle-num">{product.expected_qty}</span>
          </div>
        )}
        <div className={`circle-divider ${product.expected_qty === 0 ? 'hidden' : ''}`} />
        <div className="circle-part circle-bottom">
          <span className="circle-num">{product.in_stock}</span>
        </div>
      </div>
      <div className="circle-labels">
        {product.expected_qty > 0 && <span>в заявке</span>}
        <span>на полке</span>
      </div>
    </div>
    {product.disassembled_qty > 0 && (
      <div className="unitmap-footer">+{product.disassembled_qty} разобран</div>
    )}
  </div>
);
