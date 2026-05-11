const stack = document.querySelector(".stack");
const cards = Array.from(stack.children)
  .reverse()
  .filter((child) => child.classList.contains("card"));

cards.forEach((card) => stack.appendChild(card));

function moveCard() {
  const lastCard = stack.lastElementChild;
  if (lastCard.classList.contains("card")) {
    lastCard.classList.add("swap");

    setTimeout(() => {
      lastCard.classList.remove("swap");
      stack.insertBefore(lastCard, stack.firstElementChild);
    }, 1200);
  }
}

let autoplayInterval = setInterval(moveCard, 4000);

stack.addEventListener("click", function (e) {
  const card = e.target.closest(".card");
  if (card && card === stack.lastElementChild) {
    card.classList.add("swap");

    setTimeout(() => {
      card.classList.remove("swap");
      stack.insertBefore(card, stack.firstElementChild);
    }, 1200);
  }
});

function renderTopVendidos(items) {
  const container = document.getElementById('top-vendidos');
  if (!container) return;
  if (!Array.isArray(items) || items.length === 0) {
    container.innerHTML = '<div class="loading">Nenhum top vendido encontrado.</div>';
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="top-venda-card">
      <img src="${item.imagem_url}" alt="${item.nome}" />
      <div class="top-venda-content">
        <strong>${item.nome}</strong>
        <span>${item.categoria}</span>
        <span>${item.tamanho || 'P'}</span>
        <span>Vendas: ${item.vendas || 0}</span>
      </div>
    </div>
  `).join('');
}

function fetchTopVendidos() {
  const container = document.getElementById('top-vendidos');
  if (container) container.innerHTML = '<div class="loading">Carregando os mais vendidos...</div>';

  fetch('/api/top_vendidos/?top_n=10')
    .then((response) => response.ok ? response.json() : Promise.reject(response))
    .then((data) => renderTopVendidos(data || []))
    .catch((error) => {
      console.error('Erro ao buscar top vendidos:', error);
      const container = document.getElementById('top-vendidos');
      if (container) container.innerHTML = '<div class="loading">Falha ao carregar os mais vendidos.</div>';
    });
}

fetchTopVendidos();
