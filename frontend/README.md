# Frontend Next.js

Este diretório contém um app Next.js responsável pela interface de filtros e pesquisa de catálogo.

## Como rodar

1. Abra um terminal em `frontend/`
2. Execute `npm install`
3. Execute `npm run dev`

O app usa uma regra de rewrite para encaminhar `/api/*` para `http://localhost:8000/api/*`.

## Ponto de entrada

- `pages/index.jsx`: UI da barra lateral de filtros e chamadas ao backend.
- `styles/globals.css`: estilos básicos da aplicação.
