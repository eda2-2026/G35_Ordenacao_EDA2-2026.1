from typing import Any, Dict, Iterable, List, Optional, Union

CategoryInput = Union[str, int, Iterable[str]]

CATEGORY_MAPPING = {
    'bolo': 'Bolos',
    'bolos': 'Bolos',
    'docinho': 'Doces',
    'docinhos': 'Doces',
    'doce': 'Doces',
    'doces': 'Doces',
    'cupcake': 'Cupcakes',
    'cupcakes': 'Cupcakes',
    'bolo no pote': 'Bolos no Pote',
    'bolos no pote': 'Bolos no Pote',
    'pote': 'Bolos no Pote',
    'brownie': 'Outros',
    'outros': 'Outros',
}

SIZE_MAPPING = {
    'p': 'P',
    'pequeno': 'P',
    'pequena': 'P',
    'm': 'M',
    'medio': 'M',
    'médio': 'M',
    'média': 'M',
    'g': 'G',
    'grande': 'G',
}


def _to_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    value_str = str(value).strip()
    if not value_str:
        return []
    if ',' in value_str:
        return [item.strip() for item in value_str.split(',') if item.strip()]
    return [value_str]


def _normalize_category(value: str) -> str:
    key = value.strip().lower()
    return CATEGORY_MAPPING.get(key, value.strip().title())


def _normalize_size(value: str) -> Optional[str]:
    key = value.strip().lower()
    return SIZE_MAPPING.get(key)


def _normalize_sabor(value: str) -> str:
    return value.strip().lower()


def _parse_min_rating(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        number = float(value)
        return number if number >= 0 else None
    except (TypeError, ValueError):
        return None


def filtrar_catalogo(params: Dict[str, Any], lista: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aplica filtros em O(N) sobre uma lista de dicionários antes de ordenar."""
    categories = []
    if params.get('categories') is not None:
        categories = _to_list(params.get('categories'))
    elif params.get('categoria') is not None:
        categories = _to_list(params.get('categoria'))

    sizes = []
    if params.get('sizes') is not None:
        sizes = _to_list(params.get('sizes'))
    elif params.get('tamanho') is not None:
        sizes = _to_list(params.get('tamanho'))

    sabores = []
    if params.get('sabores') is not None:
        sabores = _to_list(params.get('sabores'))
    elif params.get('sabor') is not None:
        sabores = _to_list(params.get('sabor'))

    min_rating = _parse_min_rating(params.get('min_rating') or params.get('avaliacao'))

    normalized_categories = [_normalize_category(value) for value in categories if value]
    normalized_sizes = [_normalize_size(value) for value in sizes if value]
    normalized_sizes = [value for value in normalized_sizes if value]
    normalized_sabores = [_normalize_sabor(value) for value in sabores if value]

    filtered = []
    for item in lista:
        if normalized_categories:
            if not item.get('categoria') or item.get('categoria') not in normalized_categories:
                continue

        if normalized_sizes:
            if not item.get('tamanho') or item.get('tamanho') not in normalized_sizes:
                continue

        if normalized_sabores:
            sabor_value = str(item.get('nome', '') or item.get('sabor', '')).lower()
            if not any(sabor in sabor_value for sabor in normalized_sabores):
                continue

        if min_rating is not None:
            nota = item.get('media_notas')
            if nota is None or float(nota) < min_rating:
                continue

        filtered.append(item)

    return filtered
