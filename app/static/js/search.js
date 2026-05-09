
(function () {
  'use strict';

  const DEBOUNCE_MS = 300;
  const MIN_CHARS = 2;

  // utilitários 
  function debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  
  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .search-wrapper {
        position: relative;
        display: inline-block;
      }

      #search-suggestions {
        position: absolute;
        top: calc(100% + 4px);
        left: 0;
        width: 100%;
        min-width: 260px;
        margin: 0;
        padding: 6px 0;
        list-style: none;
        background: #ffffff;
        border: 1.5px solid #f0a8c0;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(210, 98, 116, 0.15);
        max-height: 280px;
        overflow-y: auto;
        z-index: 3000;
        animation: fadeIn .15s ease;
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-6px); }
        to   { opacity: 1; transform: translateY(0); }
      }

      #search-suggestions li {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 16px;
        font-family: 'Quicksand', sans-serif;
        font-size: .95rem;
        font-weight: 500;
        color: #3d1a24;
        cursor: pointer;
        transition: background .13s, color .13s;
        border-radius: 8px;
        margin: 2px 6px;
      }

      #search-suggestions li::before {
        font-size: .85rem;
        flex-shrink: 0;
      }

      #search-suggestions li:hover,
      #search-suggestions li[aria-selected="true"] {
        background: #fde8ef;
        color: #c0385a;
      }

      #search-suggestions li span.highlight {
        color: #c0385a;
        font-weight: 700;
      }

      #search-suggestions::-webkit-scrollbar {
        width: 5px;
      }
      #search-suggestions::-webkit-scrollbar-track {
        background: transparent;
      }
      #search-suggestions::-webkit-scrollbar-thumb {
        background: #f0a8c0;
        border-radius: 10px;
      }

      .suggestion-empty {
        padding: 12px 16px;
        font-family: 'Quicksand', sans-serif;
        font-size: .9rem;
        color: #aaa;
        text-align: center;
        font-style: italic;
      }
    `;
    document.head.appendChild(style);
  }

  
  function highlightMatch(text, query) {
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return document.createTextNode(text);

    const frag = document.createDocumentFragment();
    if (idx > 0) frag.appendChild(document.createTextNode(text.slice(0, idx)));

    const mark = document.createElement('span');
    mark.className = 'highlight';
    mark.textContent = text.slice(idx, idx + query.length);
    frag.appendChild(mark);

    if (idx + query.length < text.length)
      frag.appendChild(document.createTextNode(text.slice(idx + query.length)));

    return frag;
  }

  // criar dropdown 
  function createDropdown(input) {
  
    const wrapper = document.createElement('div');
    wrapper.className = 'search-wrapper';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const ul = document.createElement('ul');
    ul.id = 'search-suggestions';
    ul.setAttribute('role', 'listbox');
    ul.style.display = 'none';
    wrapper.appendChild(ul);

    return ul;
  }

  // renderizar sugestões 
  function renderSuggestions(ul, suggestions, query) {
    ul.innerHTML = '';

    if (!suggestions.length) {
      ul.style.display = 'none';
      return;
    }

    suggestions.forEach((text) => {
      const li = document.createElement('li');
      li.setAttribute('role', 'option');
      li.appendChild(highlightMatch(text, query));
      ul.appendChild(li);
    });

    ul.style.display = 'block';
  }

  // fetch 
  async function fetchSuggestions(prefix) {
    try {
      const res = await fetch(`/autocomplete/?q=${encodeURIComponent(prefix)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      if (!res.ok) return [];
      const data = await res.json();
      return Array.isArray(data.suggestions) ? data.suggestions : [];
    } catch {
      return [];
    }
  }

  // inicialização 
  function init() {
    const input = document.getElementById('search');
    if (!input) return;

    injectStyles();
    const ul = createDropdown(input);

    const onInput = debounce(async function () {
      const q = input.value.trim();
      if (q.length < MIN_CHARS) { ul.style.display = 'none'; return; }
      const suggestions = await fetchSuggestions(q);
      renderSuggestions(ul, suggestions, q);
    }, DEBOUNCE_MS);

    input.addEventListener('input', onInput);

    input.addEventListener('blur', () => {
      setTimeout(() => { ul.style.display = 'none'; }, 160);
    });

    input.addEventListener('focus', () => {
      if (ul.children.length > 0) ul.style.display = 'block';
    });

    // clique nas sugestões
    ul.addEventListener('mousedown', (e) => {
      const li = e.target.closest('li');
      if (!li) return;
      e.preventDefault();
      selectSuggestion(li.textContent, ul, input);
    });
  }

  function selectSuggestion(text, ul, input) {
    input.value = text;
    ul.style.display = 'none';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    const btn = document.getElementById('search-btn');
    if (btn) btn.click();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
