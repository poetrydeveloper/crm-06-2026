// frontend/src/components/atomic/CategoryTree.tsx
import React, { useState } from 'react';

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
  onEditCategory?: (id: number) => void;
  onDeleteCategory?: (id: number) => void;
  readonly?: boolean;
}

const CategoryNode: React.FC<{
  category: Category;
  allCategories: Category[];
  selectedCategoryId: number | null;
  depth: number;
  collapsed: Set<number>;
  onToggleCollapse: (id: number) => void;
  onSelectCategory: (id: number) => void;
  onEditCategory?: (id: number) => void;
  onDeleteCategory?: (id: number) => void;
  readonly?: boolean;
}> = ({
  category, allCategories, selectedCategoryId, depth, collapsed,
  onToggleCollapse, onSelectCategory, onEditCategory, onDeleteCategory, readonly,
}) => {
  const validCategories = Array.isArray(allCategories) ? allCategories : [];
  const children = validCategories.filter((c) => c.parent_id === category.id);
  const isSelected = selectedCategoryId === category.id;
  const isCollapsed = collapsed.has(category.id);
  const hasChildren = children.length > 0;
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
      >
        <div
          className="d-flex align-center gap-4"
          style={{ flex: 1 }}
          onClick={() => onSelectCategory(category.id)}
        >
          <span
            onClick={(e) => {
              e.stopPropagation();
              if (hasChildren) onToggleCollapse(category.id);
            }}
            style={{
              cursor: hasChildren ? 'pointer' : 'default',
              width: '16px',
              fontSize: '11px',
              color: hasChildren ? 'var(--text-muted)' : 'transparent',
              flexShrink: 0,
              textAlign: 'center',
            }}
          >
            {hasChildren ? (isCollapsed ? '►' : '▼') : ''}
          </span>
          <span style={{ fontSize: depth > 0 ? '13px' : '14px', fontWeight: depth === 0 ? 600 : 400 }}>
            {depth > 0 ? '↳ ' : ''}
            {category.name.replace(/_/g, ' ')}
          </span>
        </div>

        {!readonly && (
          <div className="d-flex gap-4">
            {onEditCategory && (
              <button
                className="btn btn-sm btn-outline"
                onClick={(e) => { e.stopPropagation(); onEditCategory(category.id); }}
                style={{ padding: '2px 6px', fontSize: '12px', border: 'none' }}
              >
                ✏️
              </button>
            )}
            {onDeleteCategory && (
              <button
                className="btn btn-sm btn-outline"
                onClick={(e) => { e.stopPropagation(); onDeleteCategory(category.id); }}
                style={{ padding: '2px 6px', fontSize: '12px', border: 'none', color: 'var(--danger)' }}
              >
                🗑️
              </button>
            )}
          </div>
        )}
      </div>

      {hasChildren && !isCollapsed && (
        <ul style={{ listStyle: 'none', paddingLeft: 0, margin: 0 }}>
          {children.map((child) => (
            <CategoryNode
              key={child.id}
              category={child}
              allCategories={validCategories}
              selectedCategoryId={selectedCategoryId}
              depth={depth + 1}
              collapsed={collapsed}
              onToggleCollapse={onToggleCollapse}
              onSelectCategory={onSelectCategory}
              onEditCategory={onEditCategory}
              onDeleteCategory={onDeleteCategory}
              readonly={readonly}
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
  readonly = false,
}) => {
  const validCategories = Array.isArray(categories) ? categories : [];
  const rootCategories = validCategories.filter((cat) => !cat.parent_id);
  const [collapsed, setCollapsed] = useState<Set<number>>(new Set());

  const handleToggleCollapse = (id: number) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className="card" style={{ width: '280px', maxHeight: 'calc(100vh - 160px)', overflowY: 'auto', flexShrink: 0 }}>
      <div className="d-flex justify-between align-center mb-3">
        <h3 className="card-title" style={{ margin: 0, fontSize: '15px' }}>
          Категории
        </h3>
        {!readonly && (
          <button className="btn btn-success btn-sm" onClick={onCreateCategory}>
            + Добавить
          </button>
        )}
      </div>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {rootCategories.map((cat) => (
          <CategoryNode
            key={cat.id}
            category={cat}
            allCategories={validCategories}
            selectedCategoryId={selectedCategoryId}
            depth={0}
            collapsed={collapsed}
            onToggleCollapse={handleToggleCollapse}
            onSelectCategory={onSelectCategory}
            onEditCategory={onEditCategory}
            onDeleteCategory={onDeleteCategory}
            readonly={readonly}
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