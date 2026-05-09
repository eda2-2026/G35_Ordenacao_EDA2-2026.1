from abc import ABC, abstractmethod
from typing import List, Any, Callable


class Ordenador(ABC):
    """
    Classe abstrata que define a interface de um motor de ordenação.
    """

    @abstractmethod
    def ordenar(self, lista: List[Any], chave: Any, reverse: bool = False) -> List[Any]:
        raise NotImplementedError()
