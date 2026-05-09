from typing import List, Any
from .base import Ordenador


class QuickSort(Ordenador):
    """
    Implementação do Quick Sort para ordenar objetos por uma chave.
    """

    def _key(self, item: Any, chave: Any) -> Any:
        if callable(chave):
            return chave(item)
        if isinstance(chave, str):
            return item.get(chave, '')
        raise ValueError('chave deve ser string ou função')

    def ordenar(self, lista: List[Any], chave: Any, reverse: bool = False) -> List[Any]:
        # Usamos uma cópia para não mutar o original
        arr = list(lista)

        def partition(low, high):
            pivot = _key_val(high)
            i = low - 1
            for j in range(low, high):
                if _compare(_key_val(j), pivot):
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def _key_val(index):
            return self._to_str_key(self._key(arr[index], chave))

        def _compare(a, b):
            # compara dependendo de reverse
            return a <= b if not reverse else a >= b

        def _quicksort(low, high):
            if low < high:
                pi = partition(low, high)
                _quicksort(low, pi - 1)
                _quicksort(pi + 1, high)

        _quicksort(0, len(arr) - 1)
        return arr

    def _to_str_key(self, value: Any) -> str:
        # Garantimos comparação case-insensitive para nomes
        if isinstance(value, str):
            return value.lower()
        return str(value)
