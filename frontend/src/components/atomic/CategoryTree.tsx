// frontend/src/components/atomic/CategoryTree.tsx
import React from 'react';

interface Category {
  id: number;
  name: string;
  parent_id: number | null;
}

interface CategoryTreeProps {
  categories: Category[];
  selectedCategoryId: number | null;
  onSelectCategory: (id: number) => void;
  onCreateCategory: () => void;
  onEditCategory: (id: number) => void;
  onDeleteCategory: (id: number) => void;
}

// 🔄 Рекурсивный компонент для отрисовки категории и её потомков
const CategoryNode: React.FC<{
  category: Category;
  allCategories: Category[];
  selectedCategoryId: number | null;
  depth: number;
  onSelectCategory: (id: number) => void;
  onEditCategory: (id: number) => void;
  onDeleteCategory: (id: number) => void;
}> = ({ category, allCategories, selectedCategoryId, depth, onSelectCategory, onEditCategory, onDeleteCategory }) => {
  const MAX_DEPTH = 20;
  const children = allCategories.filter(c => c.parent_id === category.id);
  const isSelected = selectedCategoryId === category.id;
  const indent = depth * 15;

  return (
    <li style={{ marginBottom: '4px' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '5px 6px',
          borderRadius: '4px',
          background: isSelected ? '#2d2d2d' : 'transparent',
          cursor: 'pointer',
          marginLeft: `${indent}px`
        }}
        onClick={() => onSelectCategory(category.id)}
      >
        <span style={{ fontSize: depth > 0 ? '14px' : '15px', color: isSelected ? '#4fa8ff' : depth > 0 ? '#ccc' : '#fff' }}>
          {depth > 0 ? '↳ ' : ''}{category.name}
        </span>
        <div style={{ display: 'flex', gap: '4px' }}>
          <button
            onClick={(e) => { e.stopPropagation(); onEditCategory(category.id); }}
            style={{ background: 'none', border: 'none', color: '#aaa', cursor: 'pointer', fontSize: '12px' }}
          >
            ✏️
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDeleteCategory(category.id); }}
            style={{ background: 'none', border: 'none', color: '#ff4d4d', cursor: 'pointer', fontSize: '12px' }}
          >
            🗑️
          </button>
        </div>
      </div>

      {/* Рекурсивно рендерим детей, если не превышен лимит глубины */}
      {depth < MAX_DEPTH && children.length > 0 && (
        <ul style={{ listStyleType: 'none', paddingLeft: 0, margin: 0 }}>
          {children.map(child => (
            <CategoryNode
              key={child.id}
              category={child}
              allCategories={allCategories}
              selectedCategoryId={selectedCategoryId}
              depth={depth + 1}
              onSelectCategory={onSelectCategory}
              onEditCategory={onEditCategory}
              onDeleteCategory={onDeleteCategory}
            />
          ))}
        </ul>
      )}
    </li>
  );
};

export const CategoryTree: React.FC<CategoryTreeProps> = ({
  categories,
  selectedCategoryId,
  onSelectCategory,
  onCreateCategory,
  onEditCategory,
  onDeleteCategory,
}) => {
  const rootCategories = categories.filter(cat => !cat.parent_id);

  return (
    <div style={{ width: '280px', background: '#1a1a1a', padding: '15px', borderRight: '1px solid #333', overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: 0, color: '#4fa8ff' }}>📁 Категории</h3>
        <button
          onClick={onCreateCategory}
          style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}
        >
          + Добавить
        </button>
      </div>
      <ul style={{ listStyleType: 'none', paddingLeft: 0, margin: 0 }}>
        {rootCategories.map(cat => (
          <CategoryNode
            key={cat.id}
            category={cat}
            allCategories={categories}
            selectedCategoryId={selectedCategoryId}
            depth={0}
            onSelectCategory={onSelectCategory}
            onEditCategory={onEditCategory}
            onDeleteCategory={onDeleteCategory}
          />
        ))}
      </ul>
    </div>
  );
};