// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import './App.css';

interface Brand { id: number; name: string; }
interface Category { id: number; name: string; parent_id: number | null; }
interface Supplier { id: number; name: string; }
interface Product {
  id: number;
  code: string;
  name: string;
  brand_name: string;
  category_name: string;
  recommended_retail_price: number;
  search_tags: string[];
}

function App() {
  // Списки из базы данных PostgreSQL
  const [brands, setBrands] = useState<Brand[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);

  // Состояния для форм ввода
  const [newBrand, setNewBrand] = useState('');
  const [newSupplier, setNewSupplier] = useState('');
  const [newCategory, setNewCategory] = useState({ name: '', parent_id: '' as any });

  // Состояние для всплывающих уведомлений
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Автоматическое скрытие уведомления через 3 секунды
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);
  
  const [newProduct, setNewProduct] = useState({
    code: '',
    name: '',
    category_id: '',
    brand_id: '',
    price: '',
    aliases: ''
  });

  // Асинхронная загрузка всех справочников через наш Nginx API Gateway
  const loadData = async () => {
    try {
      const resBrands = await fetch('/api/v1/catalog/brands');
      const resCats = await fetch('/api/v1/catalog/categories');
      const resSups = await fetch('/api/v1/warehouse/suppliers');
      const resProds = await fetch('/api/v1/catalog/products/all');

      if (resBrands.ok) setBrands(await resBrands.json());
      if (resCats.ok) setCategories(await resCats.json());
      if (resSups.ok) setSuppliers(await resSups.json());
      if (resProds.ok) setProducts(await resProds.json());
    } catch (e) {
      console.error("Ошибка запроса к API ядра через Nginx", e);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleCreateBrand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBrand) return;
    try {
      const res = await fetch('/api/v1/catalog/brands', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newBrand })
      });
      if (res.ok) {
        setNotification({ message: `Бренд "${newBrand}" успешно создан!`, type: 'success' });
        setNewBrand('');
        loadData(); // Сразу обновляем списки в выпадающих окнах
      } else {
        const err = await res.json();
        setNotification({ message: err.detail || "Ошибка создания бренда", type: 'error' });
      }
    } catch (err) {
      setNotification({ message: "Нет связи с сервером", type: 'error' });
    }
  };

  const handleCreateSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSupplier) return;
    try {
      const res = await fetch('/api/v1/warehouse/suppliers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newSupplier })
      });
      if (res.ok) {
        setNotification({ message: `Поставщик "${newSupplier}" добавлен в систему!`, type: 'success' });
        setNewSupplier('');
        loadData();
      } else {
        const err = await res.json();
        setNotification({ message: err.detail || "Ошибка создания поставщика", type: 'error' });
      }
    } catch (err) {
      setNotification({ message: "Нет связи с сервером", type: 'error' });
    }
  };

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCategory.name) return;
    try {
      const res = await fetch('/api/v1/catalog/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newCategory.name,
          parent_id: newCategory.parent_id ? parseInt(newCategory.parent_id) : null
        })
      });
      if (res.ok) {
        setNotification({ message: `Категория "${newCategory.name}" создана!`, type: 'success' });
        setNewCategory({ name: '', parent_id: '' });
        loadData();
      } else {
        setNotification({ message: "Ошибка создания категории", type: 'error' });
      }
    } catch (err) {
      setNotification({ message: "Нет связи с сервером", type: 'error' });
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProduct.name || !newProduct.code || !newProduct.category_id) {
      setNotification({ message: "Заполните обязательные поля: Артикул, Имя, Категория!", type: 'error' });
      return;
    }
    try {
      const res = await fetch('/api/v1/catalog/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: newProduct.code,
          name: newProduct.name,
          category_id: parseInt(newProduct.category_id),
          brand_id: newProduct.brand_id ? parseInt(newProduct.brand_id) : null,
          recommended_retail_price: newProduct.price ? parseFloat(newProduct.price) : 0,
          search_aliases: newProduct.aliases ? newProduct.aliases.split(',').map(s => s.trim()) : []
        })
      });
      if (res.ok) {
        setNotification({ message: `Товар "${newProduct.name}" успешно занесён в каталог!`, type: 'success' });
        setNewProduct({ code: '', name: '', category_id: '', brand_id: '', price: '', aliases: '' });
        loadData();
      } else {
        const err = await res.json();
        setNotification({ message: err.detail || "Такой артикул уже существует!", type: 'error' });
      }
    } catch (err) {
      setNotification({ message: "Нет связи с сервером", type: 'error' });
    }
  };
  return (
    <div className="admin-container">
      {/* ВСПЛЫВАЮЩЕЕ УВЕДОМЛЕНИЕ */}
      {notification && (
        <div className={`notification-toast ${notification.type}`}>
          {notification.type === 'success' ? '✅ ' : '❌ '}
          {notification.message}
        </div>
      )}
      <header className="admin-header"></header>
      <header className="admin-header">
        <h1>🛠️ Панель Администратора CRM: Управление Каталогом</h1>
        <button className="refresh-btn" onClick={loadData}>🔄 Обновить данные</button>
      </header>

      <div className="admin-grid">
        {/* ЛЕВАЯ КОЛОНКА: СПРАВОЧНИКИ И ДЕРЕВО КАТЕГОРИЙ */}
        <aside className="admin-sidebar card">
          <h2>1. Базовые справочники</h2>
          
          <form onSubmit={handleCreateBrand} className="mini-form">
            <input type="text" placeholder="+ Добавить Бренд" value={newBrand} onChange={e => setNewBrand(e.target.value)} />
            <button type="submit">Создать</button>
          </form>

          <form onSubmit={handleCreateSupplier} className="mini-form">
            <input type="text" placeholder="+ Добавить Поставщика" value={newSupplier} onChange={e => setNewSupplier(e.target.value)} />
            <button type="submit">Создать</button>
          </form>

          <hr />

          <h3>📁 Дерево категорий</h3>
          <form onSubmit={handleCreateCategory} className="vertical-form">
            <input type="text" placeholder="Название новой категории" value={newCategory.name} onChange={e => setNewCategory({...newCategory, name: e.target.value})} />
            <select value={newCategory.parent_id} onChange={e => setNewCategory({...newCategory, parent_id: e.target.value})}>
              <option value="">-- Сделать корневой --</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <button type="submit">Добавить категорию</button>
          </form>

          <div className="category-tree">
            {categories.filter(c => !c.parent_id).map(parent => (
              <div key={parent.id} className="tree-parent">
                📁 <strong>{parent.name}</strong> (ID: {parent.id})
                {categories.filter(child => child.parent_id === parent.id).map(child => (
                  <div key={child.id} className="tree-child">
                    📄 {child.name} (ID: {child.id})
                  </div>
                ))}
              </div>
            ))}
          </div>
        </aside>

        {/* ЦЕНТРАЛЬНАЯ ЗОНА: ФОРМА СОЗДАНИЯ ТОВАРА */}
        <main className="admin-main card">
          <h2>2. Создание Карточки Товара (Каталог)</h2>
          <form onSubmit={handleCreateProduct} className="main-product-form">
            <div className="form-group">
              <label>Артикул (Уникальный код): *</label>
              <input type="text" placeholder="Например: GCAA1201" value={newProduct.code} onChange={e => setNewProduct({...newProduct, code: e.target.value})} />
            </div>

            <div className="form-group">
              <label>Официальное Наименование: *</label>
              <input type="text" placeholder="Например: Набор ключей трещоточных Toptul" value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Поместить в категорию: *</label>
                <select value={newProduct.category_id} onChange={e => setNewProduct({...newProduct, category_id: e.target.value})}>
                  <option value="">-- Выберите категорию --</option>
                  {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label>Производитель (Бренд):</label>
                <select value={newProduct.brand_id} onChange={e => setNewProduct({...newProduct, brand_id: e.target.value})}>
                  <option value="">-- Без бренда --</option>
                  {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Рекомендуемая розничная цена (руб.):</label>
              <input type="number" placeholder="5400.00" value={newProduct.price} onChange={e => setNewProduct({...newProduct, price: e.target.value})} />
            </div>

            <div className="form-group">
              <label>Сленговые синонимы (через запятую для умного поиска):</label>
              <input type="text" placeholder="набор топтул, трещотки" value={newProduct.aliases} onChange={e => setNewProduct({...newProduct, aliases: e.target.value})} />
            </div>

            <button type="submit" className="submit-product-btn">🚀 Сохранить товар в систему</button>
          </form>
        </main>
      </div>

      {/* НИЖНЯЯ ЗОНА: НАГЛЯДНАЯ ТАБЛИЦА ВСЕХ ТОВАРОВ В БАЗЕ ДАННЫХ */}
      <section className="admin-table-section card">
        <h2>📊 Содержимое базы данных: Справочник товаров ({products.length} поз.)</h2>
        <div className="table-wrapper">
          <table className="modern-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Артикул</th>
                <th>Наименование товара</th>
                <th>Категория</th>
                <th>Бренд</th>
                <th>Розничная цена</th>
                <th>Сгенерированные авто-теги умного поиска</th>
              </tr>
            </thead>
            <tbody>
              {products.length === 0 ? (
                <tr><td colSpan={7} className="empty-row">База данных пуста. Заполните справочники и создайте первый товар выше!</td></tr>
              ) : (
                products.map(p => (
                  <tr key={p.id}>
                    <td><strong>{p.id}</strong></td>
                    <td className="code-badge">{p.code}</td>
                    <td>{p.name}</td>
                    <td><span className="cat-badge">{p.category_name}</span></td>
                    <td>{p.brand_name}</td>
                    <td className="price-text">{p.recommended_retail_price.toLocaleString()} руб.</td>
                    <td>
                      <div className="tags-container">
                        {p.search_tags?.map((t, idx) => <span key={idx} className="tag">{t}</span>)}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default App;