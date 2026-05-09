(function () {
  const e = React.createElement;
  const { useState, useEffect } = React;

  function Stars({ count }) {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(e('span', { key: i, className: i < count ? 'star on' : 'star' }, i < count ? '★' : '☆'));
    }
    return e('div', { className: 'stars' }, stars);
  }

  function RatingStars({ value, onRate }) {
    const v = Math.round(value || 0);
    const stars = [];
    for (let i = 0; i < 5; i++) {
      const filled = i < v;
      stars.push(e('span', {
        key: i,
        className: 'star ' + (filled ? 'on' : ''),
        onClick: onRate ? (() => onRate(i + 1)) : undefined,
        style: { cursor: onRate ? 'pointer' : 'default', marginRight: '4px' }
      }, filled ? '★' : '☆'));
    }
    return e('div', { className: 'rating-stars' }, stars);
  }

  function formatPreco(v) {
    return 'R$ ' + v.toFixed(2).replace('.', ',');
  }

  function CatalogApp() {
    const [items, setItems] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeSort, setActiveSort] = useState('relevancia');

    // Busca do catálogo do backend com opção de sort e filtros
    function fetchCatalog(sort, filters) {
      const params = new URLSearchParams();
      if (sort) params.set('sort', sort);
      if (filters) {
        if (filters.categories && filters.categories.length) params.set('categories', filters.categories.join(','));
        if (filters.sizes && filters.sizes.length) params.set('sizes', filters.sizes.join(','));
        if (filters.sabores && filters.sabores.length) params.set('sabores', filters.sabores.join(','));
        if (filters.min_rating) params.set('min_rating', String(filters.min_rating));
      }
      const url = '/api/catalogo/' + (params.toString() ? '?' + params.toString() : '');
      setLoading(true);
      return fetch(url, { credentials: 'same-origin' })
        .then(async (r) => {
          if (!r.ok) {
            const text = await r.text();
            console.error('Resposta inesperada do /api/catalogo/:', r.status, text);
            return [];
          }
          try {
            return await r.json();
          } catch (e) {
            const txt = await r.text();
            console.error('Não foi possível parsear JSON de /api/catalogo/:', e, txt);
            return [];
          }
        })
        .catch((err) => {
          console.error('Erro ao carregar /api/catalogo/:', err);
          return [];
        })
        .finally(() => setLoading(false));
    }

    // filtros locais
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [selectedSizes, setSelectedSizes] = useState([]);
    const [selectedSabores, setSelectedSabores] = useState([]);
    const [selectedRating, setSelectedRating] = useState(null);

    useEffect(() => {
      // Carrega inicialmente com ordenação padrão (relevância)
      const filters = { categories: selectedCategories, sizes: selectedSizes, sabores: selectedSabores, min_rating: selectedRating };
      fetchCatalog('', filters).then((data) => {
        setItems(data || []);
        setFiltered(data || []);
      });

      
      // acionem a ordenação mesmo que listeners não sejam anexados.
      window.catalogSortChanged = function (s) {
        console.log('[CatalogApp] global catalogSortChanged ->', s);
        setActiveSort(s || 'relevancia');
        const filters = { categories: selectedCategories, sizes: selectedSizes, sabores: selectedSabores, min_rating: selectedRating };
        fetchCatalog(s, filters).then((data) => {
          console.log('[CatalogApp] global fetchCatalog returned', { sort: s, length: (data || []).length });
         
          setItems(data || []);
          setFiltered(data || []);
          if (window.__updateSortIndicator) window.__updateSortIndicator(s || 'relevancia');
        });
      };
    }, []);

    function toggleCategory(cat) {
      setSelectedCategories(prev => {
        const next = prev.includes(cat) ? prev.filter(c => c !== cat) : prev.concat(cat);
        
        fetchCatalog(activeSort, { categories: next, sizes: selectedSizes, sabores: selectedSabores, min_rating: selectedRating }).then(d => { setItems(d || []); setFiltered(d || []); });
        return next;
      });
    }

    function toggleSize(sz) {
      setSelectedSizes(prev => {
        const next = prev.includes(sz) ? prev.filter(s => s !== sz) : prev.concat(sz);
        fetchCatalog(activeSort, { categories: selectedCategories, sizes: next, sabores: selectedSabores, min_rating: selectedRating }).then(d => { setItems(d || []); setFiltered(d || []); });
        return next;
      });
    }

    function toggleSabor(sb) {
      setSelectedSabores(prev => {
        const next = prev.includes(sb) ? prev.filter(s => s !== sb) : prev.concat(sb);
        fetchCatalog(activeSort, { categories: selectedCategories, sizes: selectedSizes, sabores: next, min_rating: selectedRating }).then(d => { setItems(d || []); setFiltered(d || []); });
        return next;
      });
    }

    function setRating(r) {
      setSelectedRating(r);
      fetchCatalog(activeSort, { categories: selectedCategories, sizes: selectedSizes, sabores: selectedSabores, min_rating: r }).then(d => { setItems(d || []); setFiltered(d || []); });
    }

    // Função para adicionar item ao carrinho 
    function getCookie(name) {
      const v = document.cookie.match('(^|;)\s*' + name + '\s*=\s*([^;]+)');
      return v ? v.pop() : null;
    }

    function addToCart(p) {
      const meta = document.querySelector('meta[name="csrf-token"]');
      const csrf = meta ? meta.getAttribute('content') : getCookie('csrftoken');
      const payload = {
        bolo_id: p.id,
        tamanho: (p.tamanho || 'P').toUpperCase(),
        bolo_nome: p.nome,
        preco: p.preco
      };

      
      const authToken = localStorage.getItem('authToken') || localStorage.getItem('token') || localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json'
      };
      if (csrf) headers['X-CSRFToken'] = csrf;
      if (authToken) headers['Authorization'] = 'Bearer ' + authToken;

      fetch('/adicionar_ao_carrinho/', {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify(payload)
      })
      .then(async (response) => {
        if (response.status === 401 || response.status === 403) {
          alert('Você precisa estar logado para adicionar itens ao carrinho. Redirecionando para login...');
          window.location.href = '/';
          throw new Error('Not authenticated');
        }
        const ct = response.headers.get('content-type') || '';
        if (!ct.includes('application/json')) {
          const txt = await response.text();
          console.warn('Resposta inesperada (não JSON) de /adicionar_ao_carrinho/:', response.status, txt);
          throw new Error('non-json');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          if (window.atualizarCarrinho) {
            window.atualizarCarrinho();
          } else {
            console.warn('window.atualizarCarrinho não encontrada; usando fallback para atualizar sidebar.');
            refreshSidebarCart();
          }
        } else {
          console.error('Erro ao adicionar (resposta):', data);
          alert('Erro ao adicionar item ao carrinho.');
        }
      })
      .catch(err => {
        if (err.message === 'Not authenticated') return;
        if (err.message === 'non-json') return;
        console.error('Erro ao adicionar ao carrinho:', err);
        alert('Erro ao adicionar item ao carrinho.');
      });
    }

    function refreshSidebarCart() {
      fetch('/obter_carrinho/', { credentials: 'same-origin' })
        .then(r => {
          const ct = r.headers.get('content-type') || '';
          if (!ct.includes('application/json')) {
            console.warn('Resposta não-JSON ao obter_carrinho; abortando refreshSidebarCart.');
            return null;
          }
          return r.json();
        })
        .then(data => {
          if (!data) return;
          const carrinhoItens = document.getElementById('carrinho-itens');
          const totalElem = document.getElementById('total');
          if (!carrinhoItens) return;
          carrinhoItens.innerHTML = '';
          (data.carrinho || []).forEach(item => {
            const div = document.createElement('div');
            div.className = 'carrinho-item';
            div.innerHTML = `
              <img src="${item.imagem_url}" alt="${item.bolo_nome}" class="cart-img">
              <div class="carrinho-item-info"><strong>${item.bolo_nome}</strong> <span>(${item.tamanho})</span>
                <div>R$ ${Number(item.preco).toFixed(2)} x ${item.quantidade}</div>
              </div>`;
            carrinhoItens.appendChild(div);
          });
          if (totalElem && typeof data.total !== 'undefined') {
            totalElem.textContent = `R$ ${parseFloat(data.total).toFixed(2)}`;
          }
        })
        .catch(err => console.error('Erro ao atualizar sidebar do carrinho:', err));
    }

    useEffect(() => {
      let mounted = true;
      let retries = 0;

      function filterAndSet(list) {
        const searchEl = document.getElementById('search');
        const sortEl = document.getElementById('sort-select');
        const q = (searchEl && searchEl.value || '').toLowerCase();
        const sort = sortEl ? sortEl.value : 'relevancia';
        setActiveSort(sort || 'relevancia');
        
        let res = (list || []).filter((it) => (it.nome || '').toString().toLowerCase().includes(q) || (String(it.tamanho || '')).toLowerCase().includes(q));
        
        
        console.debug('[CatalogApp] filterAndSet', { sort, q, count: res.length });
        setFiltered(res);
      }

      function applyFilters() {
        filterAndSet(items);
      }

      function tryAttach() {
        const searchEl = document.getElementById('search');
        const sortEl = document.getElementById('sort-select');
        if (searchEl && sortEl) {
          searchEl.removeEventListener('input', applyFilters);
          sortEl.removeEventListener('change', applyFilters);
          searchEl.addEventListener('input', applyFilters);
          // Quando a opção de ordenação mudar, pedimos ao backend o catálogo ordenado
            sortEl.addEventListener('change', function () {
            const s = sortEl.value || '';
            console.log('[CatalogApp] sort change ->', s);
            fetchCatalog(s).then((data) => {
              console.log('[CatalogApp] fetchCatalog returned', { sort: s, length: (data || []).length, sample: (data || [])[0] });
              setItems(data || []);
              // aplica filtro de busca sobre os novos itens diretamente com a lista retornada
              filterAndSet(data || []);
            });
          });
          
          filterAndSet(items);
        } else if (retries < 5) {
          retries += 1;
          setTimeout(tryAttach, 200);
        } else {
          
          applyFilters();
        }
      }

      if (mounted) tryAttach();

      return () => {
        mounted = false;
        const searchEl = document.getElementById('search');
        const sortEl = document.getElementById('sort-select');
        if (searchEl) searchEl.removeEventListener('input', applyFilters);
        if (sortEl) sortEl.removeEventListener('change', applyFilters);
      };
    }, [items]);

        const cards = filtered.map((p) => {
          function rate(nota) {
            // send POST to /api/avaliacoes/
            const meta = document.querySelector('meta[name="csrf-token"]');
            const csrf = meta ? meta.getAttribute('content') : (getCookie('csrftoken') || '');
            const payload = { produto_id: p.id, nota };
            fetch('/api/avaliacoes/', {
              method: 'POST',
              credentials: 'include',
              headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
              body: JSON.stringify(payload)
            }).then(r => r.json()).then(data => {
              if (data && data.success) {
                // update local item media_notas
                setFiltered(prev => prev.map(it => it.id === p.id ? Object.assign({}, it, { media_notas: data.media_notas }) : it));
                setItems(prev => prev.map(it => it.id === p.id ? Object.assign({}, it, { media_notas: data.media_notas }) : it));
              } else {
                console.error('Erro ao enviar avaliacao', data);
              }
            }).catch(err => console.error('Erro ao enviar avaliacao', err));
          }

          return e('div', { key: p.id, className: 'card' },
            e('img', { src: p.imagem_url, alt: p.nome, className: 'card-image' }),
            e('div', { className: 'card-body' },
              e('h3', null, p.nome),
              e(RatingStars, { value: p.media_notas || 0, onRate: rate }),
              e('p', { className: 'tamanho' }, 'Tamanho: ' + (p.tamanho || '')),
              e('p', { className: 'preco' }, formatPreco(p.preco))
            ),
            e('button', { onClick: () => addToCart(p), className: 'botao-comprar', 'data-product-id': p.id, 'data-product': p.nome, 'data-size': p.tamanho, 'data-price': p.preco }, 'Comprar')
          );
        });

        const children = (loading ? [e('div', { key: 'spinner', className: 'catalog-spinner' })] : []).concat(cards);

        // Sidebar filters UI (grouped and structured for vertical layout)
        const categoriesUI = ['Bolo', 'Docinho', 'Cupcake', 'Brownie'].map(cat =>
          e('div', { key: cat, className: 'filter-item' },
            e('input', { type: 'checkbox', id: `cat-${cat}`, checked: selectedCategories.includes(cat), onChange: () => toggleCategory(cat) }),
            e('label', { htmlFor: `cat-${cat}` }, cat)
          )
        );

        const sizesUI = ['Pequeno', 'Médio', 'Grande'].map(sz =>
          e('div', { key: sz, className: 'filter-item' },
            e('input', { type: 'checkbox', id: `size-${sz}`, checked: selectedSizes.includes(sz), onChange: () => toggleSize(sz) }),
            e('label', { htmlFor: `size-${sz}` }, sz)
          )
        );

        const saboresUI = ['Chocolate', 'Morango', 'Baunilha', 'Brigadeiro', 'Cenoura'].map(sb =>
          e('div', { key: sb, className: 'filter-item' },
            e('input', { type: 'checkbox', id: `sabor-${sb}`, checked: selectedSabores.includes(sb), onChange: () => toggleSabor(sb) }),
            e('label', { htmlFor: `sabor-${sb}` }, sb)
          )
        );

        const ratingOptions = [5,4,3,2,1].map(r =>
          e('div', { key: 'r' + r, className: 'filter-item' },
            e('input', { type: 'radio', name: 'rating', id: `rating-${r}`, checked: selectedRating === r, onChange: () => setRating(r) }),
            e('label', { htmlFor: `rating-${r}` }, r === 5 ? '5 estrelas' : r + ' e acima')
          )
        );

        return e('div', { className: 'catalog-layout' },
          e('aside', { className: 'catalog-sidebar' },
            e('div', { className: 'filter-group' }, e('h3', null, 'Categorias'), e('div', { className: 'filter-list' }, categoriesUI)),
            e('div', { className: 'filter-group' }, e('h3', null, 'Tamanhos'), e('div', { className: 'filter-list' }, sizesUI)),
            e('div', { className: 'filter-group' }, e('h3', null, 'Sabores'), e('div', { className: 'filter-list' }, saboresUI)),
            e('div', { className: 'filter-group' }, e('h3', null, 'Avaliação'), e('div', { className: 'filter-list' }, ratingOptions))
          ),
          e('div', { className: 'catalog-products' },
            e('div', { className: 'card-container' }, children)
          )
        );
  }

  
  document.addEventListener('DOMContentLoaded', function () {
    const root = document.getElementById('react-catalog-root');
    if (!root) return;
    ReactDOM.createRoot(root).render(e(CatalogApp));
    const sortIndicator = document.getElementById('sort-indicator');
    window.__updateSortIndicator = function (s) {
      if (!sortIndicator) return;
      const mapping = {
        'relevancia': 'Relevância',
        'az': 'A-Z',
        'za': 'Z-A',
        'menor_preco': 'Menor preço',
        'maior_preco': 'Maior preço'
      };
      sortIndicator.textContent = mapping[s] || '';
    };
  });
})();
