document.addEventListener('DOMContentLoaded', function () {
    // estado local do carrinho
    let cartState = [];

    function renderCart(cart) {
        const carrinhoItens = document.getElementById('carrinho-itens');
        const totalElem = document.getElementById('total');
        const totalItensElem = document.getElementById('total-itens');
        if (!carrinhoItens) return;

        carrinhoItens.innerHTML = '';
        let total = 0;
        let totalItens = 0;

        (cart || []).forEach(item => {
            const quantidade = Number(item.quantidade || 0);
            const preco = Number(item.preco || 0);
            total += preco * quantidade;
            totalItens += quantidade;

            const bolo = document.createElement('div');
            bolo.classList.add('item');
            bolo.innerHTML = `
                <img class="cart-img" src="${item.imagem_url}" alt="${item.bolo_nome}">
                <div class="item-details">
                    <span class="item-name">${item.bolo_nome}</span>
                    <span class="item-description">${item.descricao || ''}</span>
                    <div class="item-controls" style="display:flex; gap:8px; align-items:center; justify-content:center;">
                      <button class="qty-decrease remove-btn" data-bolo-id="${item.bolo_id}" data-tamanho="${item.tamanho}">-</button>
                      <span class="item-quantity">${quantidade}</span>
                      <button class="qty-increase" data-bolo-id="${item.bolo_id}" data-tamanho="${item.tamanho}">+</button>
                    </div>
                    <span class="item-size">${item.tamanho}</span>
                    <span class="item-price">R$ ${preco.toFixed(2)}</span>
                </div>`;

            carrinhoItens.appendChild(bolo);
        });

        if (totalElem) totalElem.textContent = `R$ ${total.toFixed(2)}`;
        if (totalItensElem) totalItensElem.textContent = totalItens;
    }

    function atualizarCarrinho() {
        fetch('/obter_carrinho/')
            .then(response => {
                const contentType = response.headers.get('content-type') || '';
                if (!contentType.includes('application/json')) {
                    console.warn('Resposta não-JSON ao obter carrinho; redirecionando para login.');
                    window.location.href = '/';
                    throw new Error('Not authenticated');
                }
                return response.json();
            })
            .then(data => {
                cartState = data.carrinho || [];
                renderCart(cartState);
            })
            .catch(error => {
                if (error.message === 'Not authenticated') return;
                console.error('Erro ao carregar o carrinho:', error);
            });
    }

    // Atualiza o carrinho quando a página é carregada
    atualizarCarrinho();

    
    window.atualizarCarrinho = atualizarCarrinho;

    
    const carrinhoRoot = document.getElementById('carrinho-itens');
    if (carrinhoRoot) {
        carrinhoRoot.addEventListener('click', function (ev) {
            const inc = ev.target.closest('.qty-increase');
            const dec = ev.target.closest('.qty-decrease');
            if (!inc && !dec) return;
            ev.preventDefault();
            if (inc) {
                const boloId = inc.getAttribute('data-bolo-id');
                const tamanho = inc.getAttribute('data-tamanho') || 'P';
                aumentarQuantidade(boloId, tamanho);
            } else if (dec) {
                const boloId = dec.getAttribute('data-bolo-id');
                const tamanho = dec.getAttribute('data-tamanho') || 'P';
                diminuirQuantidade(boloId, tamanho);
            }
        });
    }

    
    function aumentarQuantidade(boloId, tamanho) {
        let found = false;
        cartState = cartState.map(item => {
            if (String(item.bolo_id || item.id) === String(boloId) && (item.tamanho || 'P') === (tamanho || 'P')) {
                found = true;
                return Object.assign({}, item, {quantidade: Number(item.quantidade || 0) + 1});
            }
            return item;
        });
        if (!found) {
            
            cartState.push({bolo_id: boloId, quantidade: 1, tamanho: tamanho, preco: 0, imagem_url: '', bolo_nome: ''});
        }
        renderCart(cartState);

        const authToken = localStorage.getItem('authToken') || localStorage.getItem('token') || localStorage.getItem('accessToken');
        const headers = {'Content-Type': 'application/json'};
        if (getCSRFToken()) headers['X-CSRFToken'] = getCSRFToken();
        if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
        fetch('/adicionar_ao_carrinho/', {
            method: 'POST',
            credentials: 'include',
            headers: headers,
            body: JSON.stringify({bolo_id: boloId, tamanho: tamanho})
        }).then(r => {
            if (!r.ok) atualizarCarrinho(); else atualizarCarrinho();
        }).catch(err => { console.error('Erro ao aumentar quantidade:', err); atualizarCarrinho(); });
    }

    
    function diminuirQuantidade(boloId, tamanho) {
        cartState = cartState.reduce((acc, item) => {
            if (String(item.bolo_id || item.id) === String(boloId) && (item.tamanho || 'P') === (tamanho || 'P')) {
                const q = Number(item.quantidade || 0) - 1;
                if (q > 0) acc.push(Object.assign({}, item, {quantidade: q}));
               
            } else {
                acc.push(item);
            }
            return acc;
        }, []);
        renderCart(cartState);

        const authToken = localStorage.getItem('authToken') || localStorage.getItem('token') || localStorage.getItem('accessToken');
        const headers = {'Content-Type': 'application/json'};
        if (getCSRFToken()) headers['X-CSRFToken'] = getCSRFToken();
        if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
        fetch('/remover_do_carrinho/', {
            method: 'POST',
            credentials: 'include',
            headers: headers,
            body: JSON.stringify({bolo_id: boloId, tamanho: tamanho})
        }).then(r => {
            if (!r.ok) atualizarCarrinho(); else atualizarCarrinho();
        }).catch(err => { console.error('Erro ao diminuir quantidade:', err); atualizarCarrinho(); });
    }

    // Função para finalizar o pedido
    const finalizarCompraBtn = document.getElementById('finalizar-compra');
    if (finalizarCompraBtn) {
        finalizarCompraBtn.addEventListener('click', function () {
        fetch('/finalizar_compra/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),  // Função para obter o CSRF token
                'Content-Type': 'application/json'
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Pedido finalizado com sucesso!');
                window.location.reload();  // Recarrega a página
            } else {
                alert('Erro ao finalizar o pedido.');
            }
        })
        .catch(error => console.error('Erro ao finalizar o pedido:', error));
        });
    }

    // Função para obter o CSRF token
    function getCSRFToken() {
        let csrfToken = null;
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrfToken = value;
            }
        });
        return csrfToken;
    }
});
