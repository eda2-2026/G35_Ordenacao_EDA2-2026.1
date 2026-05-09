import os
import json

from django.core.management.base import BaseCommand

from loja.models import Bolo
from loja.utils.trie import Trie
from loja.trie_store import save_trie


class Command(BaseCommand):
    help = 'Constrói a trie de busca a partir dos bolos cadastrados.'

    def handle(self, *args, **options):
        self.stdout.write('Construindo trie a partir do banco...')
        t = Trie()
        count = 0
        for bolo in Bolo.objects.all():
            payload = {'id': bolo.id, 'label': bolo.sabor}
            t.insert(str(bolo.sabor), payload)
            count += 1

        # salva usando helper
        save_trie(t)

        self.stdout.write(self.style.SUCCESS(f'Trie construída com {count} bolos.'))
