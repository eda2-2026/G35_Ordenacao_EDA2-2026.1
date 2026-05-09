"""
Módulo para guardar a instância da arvore Trie usada pela aplicação.
"""
import os
import json
from typing import Optional

from .utils.trie import Trie

_TRIE: Optional[Trie] = None


def get_trie(data_path: Optional[str] = None) -> Trie:
    global _TRIE
    if _TRIE is not None:
        return _TRIE

    if data_path is None:
        base = os.path.dirname(__file__)
        data_path = os.path.join(base, 'staticdata', 'trie.json')

    t = Trie()
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            t = Trie.from_dict(data)
        except Exception:

            t = Trie()

    _TRIE = t
    return _TRIE


def save_trie(trie: Trie, data_path: Optional[str] = None) -> None:
    """Serializa e salva a trie em disco."""
    if data_path is None:
        base = os.path.dirname(__file__)
        data_path = os.path.join(base, 'staticdata', 'trie.json')

    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(trie.to_dict(), f, ensure_ascii=False)

    # atualizar cache em memória
    global _TRIE
    _TRIE = trie
