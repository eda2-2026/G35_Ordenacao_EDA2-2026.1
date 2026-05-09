from django.test import TestCase

from .utils.trie import Trie


class TrieTests(TestCase):
	def test_insert_and_search_exact(self):
		t = Trie()
		payload = {'id': 1, 'label': 'Bolo de Cenoura'}
		t.insert('Bolo de Cenoura', payload)
		res = t.search('Bolo de Cenoura')
		self.assertEqual(len(res), 1)
		self.assertEqual(res[0]['label'], 'Bolo de Cenoura')

	def test_prefix_search_and_limit(self):
		t = Trie()
		for i, name in enumerate(['Cenoura', 'Cenourinha', 'Cenourao', 'Chocolate']):
			t.insert(f'Bolo de {name}', {'id': i, 'label': f'Bolo de {name}'})

		results = t.starts_with('Bolo de Cen', limit=2)
		
		self.assertTrue(len(results) <= 2)
		
		labels = [r['label'] for r in results]
		for lab in labels:
			self.assertTrue('bolo de cen' in lab.lower())

	def test_remove(self):
		t = Trie()
		t.insert('Bolo de Milho', {'id': 10, 'label': 'Bolo de Milho'})
		ok = t.remove('Bolo de Milho')
		self.assertTrue(ok)
		self.assertEqual(t.search('Bolo de Milho'), [])

	def test_normalization(self):
		t = Trie()
		t.insert('Bolo de Fubá', {'id': 20, 'label': 'Bolo de Fubá'})
		
		res = t.starts_with('fuba')
		self.assertTrue(len(res) >= 1)
		self.assertEqual(res[0]['label'], 'Bolo de Fubá')

	def test_serialize_deserialize(self):
		t = Trie()
		t.insert('Bolo de Laranja', {'id': 5, 'label': 'Bolo de Laranja'})
		data = t.to_dict()
		t2 = Trie.from_dict(data)
		self.assertEqual(t2.search('Bolo de Laranja')[0]['label'], 'Bolo de Laranja')

