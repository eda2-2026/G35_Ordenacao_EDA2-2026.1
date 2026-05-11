import { useEffect, useState } from 'react';

const CATEGORIES = ['Bolos', 'Doces', 'Cupcakes', 'Outros'];
const SIZES = ['P', 'M', 'G'];
const FLAVORS = ['Chocolate', 'Morango', 'Baunilha', 'Brigadeiro', 'Cenoura'];
const RATINGS = [5, 4, 3];
const SORT_OPTIONS = [
  { value: 'relevancia', label: 'Relevância' },
  { value: 'az', label: 'Nome A-Z' },
  { value: 'za', label: 'Nome Z-A' },
  { value: 'menor_preco', label: 'Menor preço' },
  { value: 'maior_preco', label: 'Maior preço' },
  { value: 'categoria', label: 'Agrupar por categoria' }
];

function buildPayload(filters, sort) {
  return {
    categories: filters.categories,
    sizes: filters.sizes,
    sabores: filters.sabores,
    min_rating: filters.min_rating,
    sort,
    group_by_categoria: sort === 'categoria'
  };
}

export default function Home() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    categories: [],
    sizes: [],
    sabores: [],
    min_rating: null
  });
  const [sort, setSort] = useState('relevancia');
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchCatalog() {
      setLoading(true);
      setError(null);
      try {
        const payload = buildPayload(filters, sort);
        const response = await fetch('/api/catalogo/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        setItems(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Erro ao buscar catálogo', err);
        setError('Não foi possível carregar o catálogo.');
      } finally {
        setLoading(false);
      }
    }
    fetchCatalog();
  }, [filters, sort]);

  const toggleArrayValue = (key, value) => {
    setFilters((current) => {
      const next = current[key].includes(value)
        ? current[key].filter((item) => item !== value)
        : [...current[key], value];
      return { ...current, [key]: next };
    });
  };

  const handleRatingChange = (value) => {
    setFilters((current) => ({ ...current, min_rating: current.min_rating === value ? null : value }));
  };

  const handleFlavorToggle = (flavor) => {
    toggleArrayValue('sabores', flavor);
  };

  return (
    <div className="page-shell">
      <aside className="sidebar">
        <h2>Filtros</h2>
        <section className="filter-group">
          <h3>Categorias</h3>
          {CATEGORIES.map((category) => (
            <label key={category} className="filter-item">
              <input
                type="checkbox"
                checked={filters.categories.includes(category)}
                onChange={() => toggleArrayValue('categories', category)}
              />
              {category}
            </label>
          ))}
        </section>

        <section className="filter-group">
          <h3>Tamanhos</h3>
          {SIZES.map((size) => (
            <label key={size} className="filter-item">
              <input
                type="checkbox"
                checked={filters.sizes.includes(size)}
                onChange={() => toggleArrayValue('sizes', size)}
              />
              {size}
            </label>
          ))}
        </section>

        <section className="filter-group">
          <h3>Sabores</h3>
          {FLAVORS.map((flavor) => (
            <label key={flavor} className="filter-item">
              <input
                type="checkbox"
                checked={filters.sabores.includes(flavor)}
                onChange={() => handleFlavorToggle(flavor)}
              />
              {flavor}
            </label>
          ))}
        </section>

        <section className="filter-group">
          <h3>Avaliação</h3>
          {RATINGS.map((rating) => (
            <label key={rating} className="filter-item">
              <input
                type="radio"
                name="rating"
                checked={filters.min_rating === rating}
                onChange={() => handleRatingChange(rating)}
              />
              {rating} e acima
            </label>
          ))}
        </section>
      </aside>

      <main className="content">
        <header className="toolbar">
          <div>
            <label htmlFor="sort-select">Ordenar:</label>
            <select id="sort-select" value={sort} onChange={(event) => setSort(event.target.value)}>
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="status-bar">
            {loading ? 'Carregando...' : `${items.length} itens encontrados`}
          </div>
        </header>

        {error ? <div className="error-banner">{error}</div> : null}

        <div className="product-grid">
          {items.map((item) => (
            <article key={item.id} className="product-card">
              <img src={item.imagem_url} alt={item.nome} className="product-image" />
              <div className="product-body">
                <h3>{item.nome}</h3>
                <p className="product-meta">Categoria: {item.categoria}</p>
                <p className="product-meta">Tamanho: {item.tamanho}</p>
                <p className="product-meta">Avaliação: {item.media_notas ?? 'N/A'}</p>
                <p className="product-price">R$ {Number(item.preco).toFixed(2)}</p>
              </div>
            </article>
          ))}
        </div>
      </main>
    </div>
  );
}
