from typing import List, Any
from .base import Ordenador


class RadixSort(Ordenador):
    """
    Radix Sort (LSD) para ordenar por `preco` que é float.
    """

    def ordenar(self, lista: List[Any], chave: Any, reverse: bool = False) -> List[Any]:
        if callable(chave):
            key_fn = chave
        elif isinstance(chave, str):
            key_fn = lambda obj: obj.get(chave, 0)
        else:
            raise ValueError('chave deve ser string ou função')

        # Transformar valores em inteiros 
        pairs = []  
        for obj in lista:
            val = key_fn(obj)
            try:
                cents = int(round(float(val) * 100))
            except Exception:
                cents = 0
            pairs.append((cents, obj))

        if not pairs:
            return []

        # Encontrar o maior número (em módulo) para saber a quantidade de dígitos
        max_val = max(p[0] for p in pairs)
        if max_val < 0:
            
            max_val = abs(min(p[0] for p in pairs))

        exp = 1
        buckets = [[] for _ in range(10)]

        # Usamos cópia para não alterar a lista original
        arr = list(pairs)

        while max_val // exp > 0:
            # Limpar buckets
            for i in range(10):
                buckets[i].clear()

            # Distribuir
            for num, obj in arr:
                digit = abs(num) // exp % 10
                buckets[digit].append((num, obj))

            # Coletar
            idx = 0
            new_arr = []
            for b in buckets:
                for item in b:
                    new_arr.append(item)
                    idx += 1

            arr = new_arr
            exp *= 10

        # Agora extrair objetos na ordem
        sorted_objs = [obj for (_, obj) in arr]

        if reverse:
            sorted_objs.reverse()

        return sorted_objs
