// frontend/src/components/atomic/CategoryTree.tsx
import React from 'react';

interface Category {
  id: int;
  name: string;
  parent_id: int | null;
}

interface CategoryTreeProps {
  categories: Category[];
  selectedCategoryId: int | null;
  onSelectCategory: (id: int) => void;
  onCreateCategory: () => void;
  onEditCategory: (id: int) => void;
  onDeleteCategory: (id: int) => void;
}

export const CategoryTree: React.FC<CategoryTreeProps> = ({
  categories,
  selectedCategoryId,
  onSelectCategory,
  onCreateCategory,
  onEditCategory,
  onDeleteCategory,
}) => {
  // Фильтруем корневые категории (у которых parent_id === null)
  const rootCategories = categories.filter(cat => !cat.parent_id);

  return (
    <div style={{ width: '280px', background: '#1a1a1a', padding: '15px', borderRight: '1px solid #333' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: 0, color: '#4fa8ff' }}>📁 Категории</h3>
        <button onClick={onCreateCategory} style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}>
          + Добавить
        </button>
      </div>
      <ul style={{ listStyleType: 'none', paddingLeft: 0, margin: 0 }}>
        {rootCategories.map(cat => (
          <li key={cat.id} style={{ marginBottom: '8px' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: '6px', 
              borderRadius: '4px',
              background: selectedCategoryId === cat.id ? '#2d2d2d' : 'transparent',
              cursor: 'pointer'
            }} onClick={() => onSelectCategory(cat.id)}>
              <span style={{ color: selectedCategoryId === cat.id ? '#4fa8ff' : '#fff' }}>{cat.name}</span>
              <div style={{ display: 'flex', gap: '5px' }}>
                <button onClick={(e) => { e.stopPropagation(); onEditCategory(cat.id); }} style={{ background: 'none', border: 'none', color: '#aaa', cursor: 'pointer' }}>✏️</button>
                <button onClick={(e) => { e.stopPropagation(); onDeleteCategory(cat.id); }} style={{ background: 'none', border: 'none', color: '#ff4d4d', cursor: 'pointer' }}>🗑️</button>
              </div>
            </div>
            
            {/* Рендеринг подкатегорий (2-й уровень) */}
            <ul style={{ listStyleType: 'none', paddingLeft: '15px', marginTop: '5px' }}>
              {categories.filter(sub => sub.parent_id === cat.id).map(sub => (
                <li key={sub.id} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '4px', 
                  borderRadius: '4px',
                  background: selectedCategoryId === sub.id ? '#2d2d2d' : 'transparent',
                  cursor: 'pointer'
                }} onClick={() => onSelectCategory(sub.id)}>
                  <span style={{ fontSize: '14px', color: selectedCategoryId === sub.id ? '#4fa8ff' : '#ccc' }}>↳ {sub.name}</span>
                  <div style={{ display: 'flex', gap: '3px' }}>
                    <button onClick={(e) => { e.stopPropagation(); onEditCategory(sub.id); }} style={{ background: 'none', border: 'none', color: '#aaa', fontSize: '12px', cursor: 'pointer' }}>✏️</button>
                    <button onClick={(e) => { e.stopPropagation(); onDeleteCategory(sub.id); }} style={{ background: 'none', border: 'none', color: '#ff4d4d', fontSize: '12px', cursor: 'pointer' }}>🗑️</button>
                  </div>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
};
