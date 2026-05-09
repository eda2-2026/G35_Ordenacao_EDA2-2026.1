"""
Implementação  de Arvore Trie para busca por prefixo.
"""
from typing import Any, Dict, List, Optional
import unicodedata


def _normalize(text: str) -> str:
    text = text.lower().strip()
    nf = unicodedata.normalize('NFD', text)
    return ''.join(ch for ch in nf if unicodedata.category(ch) != 'Mn')


class _Node:
    def __init__(self):
        self.children: Dict[str, _Node] = {}
        self.payloads: List[Any] = []  
        self.is_end: bool = False


class Trie:

    def __init__(self):
        self.root = _Node()

    def insert(self, word: str, payload: Any) -> None:
        
        key = _normalize(word)
        node = self.root
        for ch in key:
            if ch not in node.children:
                node.children[ch] = _Node()
            node = node.children[ch]
        node.is_end = True
        if payload not in node.payloads:
            node.payloads.append(payload)

    def search(self, word: str) -> List[Any]:
        key = _normalize(word)
        node = self.root
        for ch in key:
            node = node.children.get(ch)
            if node is None:
                return []
        return list(node.payloads) if node.is_end else []

    def remove(self, word: str) -> bool:
        key = _normalize(word)

        path = []  
        node = self.root
        for ch in key:
            path.append((node, ch))
            node = node.children.get(ch)
            if node is None:
                return False

        if not node.is_end:
            return False

        
        node.payloads = []
        node.is_end = False

        
        for parent, ch in reversed(path):
            child = parent.children[ch]
            if child.children or child.is_end:
                break
            del parent.children[ch]

        return True

    def starts_with(self, prefix: str, limit: int = 10) -> List[Any]:
        key = _normalize(prefix)
        node = self.root
        for ch in key:
            node = node.children.get(ch)
            if node is None:
                results: List[Any] = []

                def scan_all(n: _Node):
                    if len(results) >= limit:
                        return
                    for p in n.payloads:
                        if len(results) >= limit:
                            break
                        label = ''
                        if isinstance(p, dict):
                            label = p.get('label', '')
                        else:
                            label = str(p)
                        if key in _normalize(label):
                            if p not in results:
                                results.append(p)
                    for child in n.children.values():
                        if len(results) >= limit:
                            break
                        scan_all(child)

                scan_all(self.root)
                return results

        results: List[Any] = []

        def dfs(n: _Node):
            if len(results) >= limit:
                return
            if n.is_end:
                for p in n.payloads:
                    if len(results) >= limit:
                        break
                    results.append(p)
            for child in n.children.values():
                if len(results) >= limit:
                    break
                dfs(child)

        dfs(node)
        return results

    def to_dict(self) -> Dict:
        def node_to_dict(n: _Node):
            return {
                'payloads': list(n.payloads),
                'is_end': n.is_end,
                'children': {ch: node_to_dict(c) for ch, c in n.children.items()}
            }

        return node_to_dict(self.root)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Trie':
        def dict_to_node(d):
            n = _Node()
            n.payloads = list(d.get('payloads', []))
            n.is_end = bool(d.get('is_end', False))
            for ch, cd in d.get('children', {}).items():
                n.children[ch] = dict_to_node(cd)
            return n

        t = cls()
        t.root = dict_to_node(data)
        return t
