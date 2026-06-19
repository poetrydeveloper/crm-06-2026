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

const CategoryNode: React.FC<{
  category: Category;
  allCategories: Category[];
  selectedCategoryId: number | null;
  depth: number;
  onSelectCategory: (id: number) => void;
  onEditCategory: (id: number) => void;
  onDeleteCategory: (id: number) => void;
}> = ({ category, allCategories, selectedCategoryId, depth, onSelectCategory, onEditCategory, onDeleteCategory }) => {
  const validCategories = Array.isArray(allCategories) ? allCategories : [];
  const children = validCategories.filter((c) => c.parent_id === category.id);
  const isSelected = selectedCategoryId === category.id;
  const indent = depth * 16;

  return (
    <li style={{ marginBottom: '2px' }}>
      <div
        className={`d-flex justify-between align-center ${isSelected ? 'category-selected' : ''}`}
        style={{
          padding: '6px 10px',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
          marginLeft: `${indent}px`,
          background: isSelected ? 'var(--primary)' : 'transparent',
          color: isSelected ? '#fff' : 'var(--text)',
          transition: 'all 0.1s ease',
        }}
        onClick={() => onSelectCategory(category.id)}
      >
        <span style={{ fontSize: depth > 0 ? '13px' : '14px', fontWeight: depth === 0 ? 600 : 400 }}>
          {depth > 0 ? '↳ ' : ''}
          {category.name.replace(/_/g, ' ')}
        </span>
        <div className="d-flex gap-8">
          <button
            className="btn btn-sm btn-outline"
            onClick={(e) => {
              e.stopPropagation();
              onEditCategory(category.id);
            }}
            style={{ padding: '2px 6px', fontSize: '12px', border: 'none' }}
          >
            ✏️
          </button>
          <button
            className="btn btn-sm btn-outline"
            onClick={(e) => {
              e.stopPropagation();
              onDeleteCategory(category.id);
            }}
            style={{ padding: '2px 6px', fontSize: '12px', border: 'none', color: 'var(--danger)' }}
          >
            🗑️
          </button>
        </div>
      </div>

      {children.length > 0 && (
        <ul style={{ listStyle: 'none', paddingLeft: 0, margin: 0 }}>
          {children.map((child) => (
            <CategoryNode
              key={child.id}
              category={child}
              allCategories={validCategories}
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
  const validCategories = Array.isArray(categories) ? categories : [];
  const rootCategories = validCategories.filter((cat) => !cat.parent_id);

  return (
    <div className="card" style={{ width: '280px', maxHeight: 'calc(100vh - 160px)', overflowY: 'auto', flexShrink: 0 }}>
      <div className="d-flex justify-between align-center mb-3">
        <h3 className="card-title" style={{ margin: 0, fontSize: '15px' }}>
          Категории
        </h3>
        <button className="btn btn-success btn-sm" onClick={onCreateCategory}>
          + Добавить
        </button>
      </div>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {rootCategories.map((cat) => (
          <CategoryNode
            key={cat.id}
            category={cat}
            allCategories={validCategories}
            selectedCategoryId={selectedCategoryId}
            depth={0}
            onSelectCategory={onSelectCategory}
            onEditCategory={onEditCategory}
            onDeleteCategory={onDeleteCategory}
          />
        ))}
        {rootCategories.length === 0 && (
          <li className="text-muted text-center" style={{ padding: '20px 0' }}>
            Нет категорий
          </li>
        )}
      </ul>
    </div>
  );
};