document.addEventListener('DOMContentLoaded', function () {
    // Função para atualizar o preço dinâmico
    const tamanhoSelects = document.querySelectorAll('.tamanho-select');
    if (tamanhoSelects && tamanhoSelects.length) {
        tamanhoSelects.forEach(function (selectElement) {
            if (!selectElement) return;
            selectElement.addEventListener('change', function () {
                const selectedOption = this.options[this.selectedIndex];
                const precoAtualizado = selectedOption.getAttribute('data-preco');
                const precoElemento = this.closest('.card').querySelector('.preco-dinamico');
                if (precoElemento) precoElemento.textContent = precoAtualizado;
            });
        });
    }

    // Função para atualizar o carrinho
    function atualizarCarrinho() {
        fetch('/obter_carrinho/')
            .then(response => response.json())
            .then(data => {
                const carrinhoItens = document.getElementById('carrinho-itens');
                const totalElem = document.getElementById('total');
                const total = parseFloat(data.total);
                
                carrinhoItens.innerHTML = '';
                
                data.carrinho.forEach(item => {
                    const bolo = `<div>
                        <p>${item.bolo_nome} - ${item.tamanho} - R$ ${item.preco} x ${item.quantidade}</p>
                    </div>`;
                    carrinhoItens.innerHTML += bolo;
                });
                
                totalElem.textContent = `R$ ${total.toFixed(2)}`;
            })
            .catch(error => console.error('Erro ao carregar o carrinho:', error));
    }

    // Atualiza o carrinho quando a página é carregada
    atualizarCarrinho();

    //  adicionar item ao carrinho
    const buyButtons = document.querySelectorAll('.botao-comprar');
    if (buyButtons && buyButtons.length) {
        buyButtons.forEach(function (button) {
            if (!button) return;
            button.addEventListener('click', function () {
                const boloId = this.getAttribute('data-product-id');
                const selectElement = this.closest('.card') ? this.closest('.card').querySelector('.tamanho-select') : null;
                const tamanhoSelecionado = selectElement ? selectElement.value.toUpperCase() : (this.getAttribute('data-size') || 'P').toUpperCase();
                const sabor = this.getAttribute('data-product');
                const preco = selectElement ? selectElement.options[selectElement.selectedIndex].getAttribute('data-preco') : (this.getAttribute('data-price') || 0);

                const data = {
                    bolo_id: boloId,
                    tamanho: tamanhoSelecionado,
                    bolo_nome: sabor,
                    preco: preco
                };

                const csrfToken = getCSRFToken();

            
                const authToken = localStorage.getItem('authToken') || localStorage.getItem('token') || localStorage.getItem('accessToken');
                const headers = {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                };
                if (authToken) headers['Authorization'] = 'Bearer ' + authToken;

                fetch('/adicionar_ao_carrinho/', {
                    method: 'POST',
                    credentials: 'include',
                    body: JSON.stringify(data),
                    headers: headers
                })
                .then(async (response) => {
                    if (response.status === 401 || response.status === 403) {
                        alert('Você precisa estar logado para adicionar itens ao carrinho. Redirecionando para login...');
                        window.location.href = '/';
                        throw new Error('Not authenticated');
                    }
                    const contentType = response.headers.get('content-type') || '';
                    if (!contentType.includes('application/json')) {
                        const txt = await response.text();
                        console.warn('Resposta inesperada (não JSON) ao adicionar_ao_carrinho:', response.status, txt);
                        throw new Error('non-json');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        atualizarCarrinho();  // Atualiza o carrinho após adicionar um bolo
                    } else {
                        console.error('Resposta do servidor ao adicionar:', data);
                        alert('Erro ao adicionar bolo ao carrinho.');
                    }
                })
                .catch(error => {
                    if (error.message === 'Not authenticated') return;
                    if (error.message === 'non-json') return;
                    console.error('Erro:', error);
                    alert('Erro ao adicionar bolo ao carrinho.');
                });
            });
        });
    }
  
    // Busca por nome de bolo
    const searchInput = document.getElementById('search');
    const searchBtn = document.getElementById('search-btn');
    const cards = document.querySelectorAll('.card');

   
    function filtrarBolos() {
        const termo = searchInput ? searchInput.value.trim().toLowerCase() : '';
        cards.forEach(function (card) {
            const nome = card.querySelector('h3') ? card.querySelector('h3').textContent.toLowerCase() : '';
            card.style.display = (!termo || nome.includes(termo)) ? '' : 'none';
        });
    }

    if (searchBtn) searchBtn.addEventListener('click', filtrarBolos);
    if (searchInput) searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') filtrarBolos();
    });
    
    if (searchInput) searchInput.addEventListener('input', filtrarBolos);

    
});

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