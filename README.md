# G35_Ordenacao_EDA2-2026.1

Este projeto é uma aplicação web completa desenvolvida como trabalho prático da disciplina de **Estruturas de Dados 2 (EDA2)**. O objetivo principal foi aplicar diferentes algoritmos de ordenação e busca em um cenário real de E-commerce, resolvendo problemas de performance e filtragem de catálogo com milhões de requisições potenciais.


##  O Desafio
Criar um motor de catálogo robusto que suporte múltiplos filtros simultâneos (preço, categoria, avaliação) e ordenações complexas sem perda de performance. A arquitetura exigia que a solução aplicasse o conceito do algoritmo "certo para o trabalho certo".


##  Arquitetura e Algoritmos (Back-end)

O backend em Python/Django foi estruturado com base em **Programação Orientada a Objetos (POO)**. Criamos uma classe base `Ordenador` com um método `ordenar(lista)`. Isso forçou um contrato rigoroso, garantindo que todos os algoritmos implementados seguissem um padrão limpo e polimórfico.

A base de dados é alimentada por um Mock (`catalogo.json`) contendo os doces e suas propriedades (id, nome, preco, categoria, avaliacao, vendas).

### Os Motores de Ordenação e Busca:

* **Busca Linear $O(N)$ (Motor de Filtro):** * Implementado na função `filtrar_catalogo()`. Ele varre os dados e corta as opções que não atendem aos critérios do usuário (ex: avaliações mínimas, tamanhos) *antes* da ordenação, reduzindo drasticamente o tamanho da entrada ($N$) para os algoritmos de ordenação subsequentes.
* **Radix Sort (Ordenação por Preço):**
    * O algoritmo ideal para números. Para contornar casas decimais, a lógica multiplica o preço por 100, roda o Radix Sort nos dígitos inteiros e devolve a lista de menor para o maior preço de forma extremamente veloz.
* **Quick Sort (Ordenação A-Z):**
    * Aplicado para ordenação de strings. O algoritmo elege um pivô e organiza os itens alfabeticamente pela chave `nome`.
* **Merge Sort (Agrupamento Estável por Categoria):**
    * Algoritmo $O(N \log N)$ escolhido especificamente por sua **estabilidade**. Se a lista for previamente ordenada por preço no Radix Sort, e o usuário pedir para "Agrupar por Categoria", o Merge Sort une os "Cupcakes" mantendo os preços crescentes dentro do próprio grupo.
* **Heap Sort (Vitrine Top 10):**
    * Implementação de um Max-Heap para a página inicial. Em vez de ordenar toda a loja em $O(N \log N)$ para achar os mais vendidos, o Heap é montado com a chave `vendas` e realiza apenas 10 extrações (pops). Complexidade otimizada para vitrines.


## Interface e Experiência do Usuário (Front-end)

O Front-end foi desenvolvido com React/Next.js, separando a responsabilidade de visualização e lógica de requisições.

* **Estrutura Base e Componentização:** * Desenvolvimento do layout principal e do componente `Card` que exibe a foto genérica, título, preço formatado e sistema visual de estrelas (Avaliação).
    * Menu superior para interação direta do usuário com o motor de ordenação (Dropdown: Relevância, A-Z, Preço).
* **Barra Lateral (Sidebar) e Gerenciamento de Estado:** * Interface avançada de checkboxes (Categoria, Tamanho, Sabor) e Radio Buttons (Avaliação Mínima).
    * Utilização de *Hooks* (useState/Context) para escutar múltiplos eventos simultâneos do usuário na tela. O estado empacota todas as exigências em um objeto JSON unificado e envia via `fetch` para a API do Django, recarregando apenas a lista de cards de forma reativa.


## Como Rodar o Projeto
Subir os containers:

``docker-compose up -d --build``

<br>

Preparar o banco de dados:

``docker-compose exec web python manage.py migrate``

``docker-compose exec web python manage.py loaddata app/loja/fixtures/bolos.json``

``docker-compose exec web python manage.py createsuperuser``

<br>

Gerar a árvore de busca (Trie):

``docker-compose exec web python manage.py build_trie``

<br>

 Acessar:
 
``Acessar: http://localhost:8000``

<br>



## Vídeo

[Projeto 2 de EDA2 - Algoritmos de Ordenação ](https://www.youtube.com/watch?v=bR8PJPv3X0w)


## Integrantes da Equipe

|  |Matrícula | Aluno |  
|-- | -- | -- |
|  <div align="center"><img src="https://github.com/GeovannaUmbelino.png" alt="geovanna" width="90"></div>  | 23/2014450  | <span style="color:black;">[Geovanna Umbelino](https://github.com/GeovannaUmbelino)</span>   |
| <div align="center"><img src="https://github.com/Sunamit.png" alt="sunamita" width="90"></div> | 22/1008697  | <span style="color:black;">[Sunamita Vitória](https://github.com/Sunamit)</span>    |

