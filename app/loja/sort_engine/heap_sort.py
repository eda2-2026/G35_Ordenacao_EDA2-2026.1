from typing import Any, Callable, Dict, List, Optional, Tuple
from .base import Ordenador


class HeapSort(Ordenador):
    """Máximo Heap para extrair os top N itens sem ordenar toda a coleção."""

    def ordenar(self, lista: List[Any], chave: Any, reverse: bool = False) -> List[Any]:
        if reverse:
            return sorted(lista, key=self._get_key(chave), reverse=True)
        return sorted(lista, key=self._get_key(chave))

    def top_n(self, lista: List[Any], chave: Any, n: int = 10) -> List[Any]:
        if n <= 0:
            return []
        key_fn = self._get_key(chave)
        heap: List[Tuple[Any, Any]] = []

        for item in lista:
            heap.append((key_fn(item), item))

        self._build_max_heap(heap)
        result: List[Any] = []
        size = len(heap)

        for _ in range(min(n, size)):
            if size == 0:
                break
            result.append(heap[0][1])
            heap[0] = heap[size - 1]
            size -= 1
            heap.pop()
            self._sift_down(heap, 0, size)

        return result

    def _get_key(self, chave: Any) -> Callable[[Any], Any]:
        if callable(chave):
            return chave
        if isinstance(chave, str):
            return lambda obj: obj.get(chave, 0)
        raise ValueError('chave deve ser string ou função')

    def _build_max_heap(self, heap: List[Tuple[Any, Any]]) -> None:
        size = len(heap)
        for i in range((size // 2) - 1, -1, -1):
            self._sift_down(heap, i, size)

    def _sift_down(self, heap: List[Tuple[Any, Any]], index: int, size: int) -> None:
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index

            if left < size and heap[left][0] > heap[largest][0]:
                largest = left
            if right < size and heap[right][0] > heap[largest][0]:
                largest = right
            if largest == index:
                break
            heap[index], heap[largest] = heap[largest], heap[index]
            index = largest
