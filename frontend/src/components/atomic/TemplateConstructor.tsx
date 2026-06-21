// frontend/src/components/atomic/TemplateConstructor.tsx
import React, { useState, useEffect } from 'react';
import { CategoryTree } from './CategoryTree';

interface Category { id: number; name: string; parent_id: number | null; }
interface Product { id: number; name: string; code: string; recommended_retail_price: number; }
interface TemplateItem { child_product_id: number; product_name: string; product_code: string; quantity: number; }

interface TemplateConstructorProps {
  productId: number; productName: string; unitSerial: string;
  onBack: () => void; onSaved: () => void; onClose: () => void;
}

export const TemplateConstructor: React.FC<TemplateConstructorProps> = ({ productId, productName, unitSerial, onBack, onSaved, onClose }) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [search, setSearch] = useState('');
  const [searchRes, setSearchRes] = useState<Product[]>([]);
  const [catProds, setCatProds] = useState<Product[]>([]);
  const [items, setItems] = useState<TemplateItem[]>([]);

  useEffect(() => { fetch('/api/v1/catalog/categories').then(r => r.ok && r.json().then(setCategories)); }, []);
  useEffect(() => {
    if (search.length < 2) { setSearchRes([]); return; }
    const t = setTimeout(() => fetch(`/api/v1/catalog/search?q=${encodeURIComponent(search)}`).then(r => r.ok && r.json().then(setSearchRes)), 300);
    return () => clearTimeout(t);
  }, [search]);
  useEffect(() => {
    if (!selectedId) { setCatProds([]); return; }
    fetch('/api/v1/catalog/products/all').then(r => r.ok && r.json().then(d => setCatProds(d.filter((p: any) => p.category_id === selectedId))));
  }, [selectedId]);

  const add = (p: Product) => setItems(prev => {
    const ex = prev.find(i => i.child_product_id === p.id);
    return ex ? prev.map(i => i.child_product_id === p.id ? {...i, quantity: i.quantity+1} : i) : [...prev, {child_product_id: p.id, product_name: p.name, product_code: p.code, quantity: 1}];
  });
  const remove = (id: number) => setItems(prev => prev.filter(i => i.child_product_id !== id));
  const save = async () => {
    if (!items.length) return alert('Добавьте товары');
    for (const item of items) await fetch('/api/v1/warehouse/disassembly/template-items', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({parent_product_id: productId, child_product_id: item.child_product_id, quantity: item.quantity}) });
    alert('Шаблон сохранён'); onSaved();
  };

  const display = search ? searchRes : catProds;

  return (
    <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,background:'rgba(0,0,0,0.5)',display:'flex',alignItems:'center',justifyContent:'center',zIndex:1100}} onClick={onClose}>
      <div className="card" style={{width:'800px',maxWidth:'95vw',maxHeight:'90vh',overflowY:'auto',padding:'24px'}} onClick={e=>e.stopPropagation()}>
        <h3 style={{margin:'0 0 8px',fontSize:16,fontWeight:700}}>Создание шаблона: {productName}</h3>
        <p className="text-muted" style={{fontSize:13,marginBottom:16}}>SN: {unitSerial}</p>
        <input className="form-control mb-3" placeholder="Поиск товаров..." value={search} onChange={e=>setSearch(e.target.value)} />
        <div className="d-flex gap-16 mb-3">
          <CategoryTree categories={categories} selectedCategoryId={selectedId} onSelectCategory={id=>{setSelectedId(id);setSearch('');}} onCreateCategory={()=>{}} readonly />
          <div style={{flex:1,maxHeight:250,overflowY:'auto'}}>
            {display.length===0 ? <p className="text-muted text-center" style={{padding:20}}>{search?'Ничего не найдено':'Выберите категорию'}</p> :
              display.map(p=>(
                <div key={p.id} onClick={()=>add(p)} style={{padding:'8px 12px',borderBottom:'1px solid var(--border)',cursor:'pointer',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                  <div><div style={{fontWeight:500,textTransform:'capitalize'}}>{p.name.replace(/_/g,' ')}</div><div className="text-muted text-mono" style={{fontSize:11}}>{p.code}</div></div>
                  <span style={{fontWeight:600,color:'var(--success)'}}>{p.recommended_retail_price.toFixed(2)} ₽</span>
                </div>
              ))
            }
          </div>
        </div>
        <h4 style={{fontSize:14,fontWeight:600,marginBottom:8}}>Состав ({items.length} поз.)</h4>
        {items.length===0 ? <p className="text-muted" style={{fontSize:13}}>Добавьте товары из списка выше</p> :
          items.map(item=>(
            <div key={item.child_product_id} style={{display:'flex',alignItems:'center',padding:'6px 10px',background:'var(--bg-secondary)',borderRadius:'var(--radius-sm)',marginBottom:4}}>
              <span style={{flex:1,fontWeight:500,textTransform:'capitalize'}}>{item.product_name.replace(/_/g,' ')}</span>
              <span className="text-muted text-mono" style={{fontSize:12,marginRight:8}}>{item.product_code}</span>
              <input type="number" min="1" value={item.quantity} onChange={e=>{const v=parseInt(e.target.value)||1;setItems(prev=>prev.map(i=>i.child_product_id===item.child_product_id?{...i,quantity:v}:i))}} className="form-control" style={{width:60,textAlign:'center',marginRight:8}} />
              <button className="btn btn-sm btn-outline" onClick={()=>remove(item.child_product_id)} style={{color:'var(--danger)',border:'none'}}>✕</button>
            </div>
          ))
        }
        <div className="d-flex gap-8 mt-3">
          <button className="btn btn-outline" onClick={onBack}>Назад</button>
          <button className="btn btn-success" onClick={save} disabled={items.length===0}>Сохранить шаблон</button>
        </div>
      </div>
    </div>
  );
};