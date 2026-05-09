document.addEventListener('DOMContentLoaded', function () {

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

    
    const buyButtons = document.querySelectorAll('.botao-comprar');
    if (buyButtons && buyButtons.length) {
        buyButtons.forEach(function (button) {
            if (!button) return;
            button.addEventListener('click', function () {
                const boloId = this.getAttribute('data-product-id');
                
                const selectElement = this.closest('.card') ? this.closest('.card').querySelector('.tamanho-select') : null;
                const tamanhoSelecionado = selectElement ? selectElement.value.toUpperCase() : 'P';
                const sabor = this.getAttribute('data-product');
                const preco = selectElement ? selectElement.options[selectElement.selectedIndex].getAttribute('data-preco') : 0;

                const data = {
                    bolo_id: boloId,
                    tamanho: tamanhoSelecionado,
                    bolo_nome: sabor,
                    preco: preco
                };

                const csrfToken = getCSRFToken();

                fetch('/adicionar_ao_carrinho/', {
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        atualizarCarrinho();  
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro ao adicionar bolo ao carrinho.');
                });
            });
        });
    }
  
    
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
