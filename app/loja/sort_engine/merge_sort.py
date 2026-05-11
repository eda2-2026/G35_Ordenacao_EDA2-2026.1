from typing import Any, List
from .base import Ordenador


class MergeSort(Ordenador):
    """Merge Sort estável para agrupar itens sem quebrar ordens já existentes."""

    def ordenar(self, lista: List[Any], chave: Any, reverse: bool = False) -> List[Any]:
        if callable(chave):
            key_fn = chave
        elif isinstance(chave, str):
            key_fn = lambda obj: obj.get(chave, '')
        else:
            raise ValueError('chave deve ser string ou função')

        def _normalize(value: Any) -> Any:
            if isinstance(value, str):
                return value.lower()
            return value

        def _merge(left: List[Any], right: List[Any]) -> List[Any]:
            merged = []
            i = j = 0
            while i < len(left) and j < len(right):
                a = _normalize(key_fn(left[i]))
                b = _normalize(key_fn(right[j]))
                if reverse:
                    if a >= b:
                        merged.append(left[i]); i += 1
                    else:
                        merged.append(right[j]); j += 1
                else:
                    if a <= b:
                        merged.append(left[i]); i += 1
                    else:
                        merged.append(right[j]); j += 1
            if i < len(left):
                merged.extend(left[i:])
            if j < len(right):
                merged.extend(right[j:])
            return merged

        def _merge_sort(items: List[Any]) -> List[Any]:
            if len(items) <= 1:
                return items
            mid = len(items) // 2
            return _merge(_merge_sort(items[:mid]), _merge_sort(items[mid:]))

        return _merge_sort(list(lista))
