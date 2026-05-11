from django.core.management.base import BaseCommand
from loja.models import Bolo, Avaliacao

class Command(BaseCommand):
    help = 'Atualiza categorias dos bolos e adiciona avaliações'

    def handle(self, *args, **options):
        # Mapeamento de nomes de bolos para categorias corretas
        categorias_map = {
            'Bolo de Fubá': 'Bolos',
            'Bolo de Ninho com Morango': 'Bolos',
            'Bolo de Cenoura': 'Bolos',
            'Bolo de Chocolate': 'Bolos',
            'Bolo de Chocolate com Morango': 'Bolos',
            'Bolo de  Coco': 'Bolos',
            'Bolo de Limão': 'Bolos',
            'Bolo de abacaxi': 'Bolos',
            'Bolo de Milho': 'Bolos',
            'Bolo de Banana': 'Bolos',
            'Cupcake de Chocolate': 'Cupcakes',
            'Cupcake de Morango': 'Cupcakes',
            'Brigadeiro': 'Doces',
            'Beijinho': 'Doces',
            'Docinho de Coco': 'Doces',
        }
        
        # Avaliações a adicionar por bolo
        avaliacoes_map = {
            'Bolo de Fubá': [5, 5, 4, 5, 4],
            'Bolo de Ninho com Morango': [5, 4, 5, 4, 5],
            'Bolo de Cenoura': [4, 5, 5, 4, 5],
            'Bolo de Chocolate': [5, 5, 5, 4, 5],
            'Bolo de Chocolate com Morango': [4, 4, 5, 5, 4],
            'Bolo de  Coco': [4, 5, 4, 5, 4],
            'Bolo de Limão': [3, 4, 5, 4, 3],
            'Bolo de abacaxi': [4, 3, 4, 5, 4],
            'Bolo de Milho': [3, 4, 4, 3, 4],
            'Bolo de Banana': [3, 3, 4, 3, 4],
            'Cupcake de Chocolate': [5, 5, 4, 5, 5],
            'Cupcake de Morango': [4, 5, 5, 4, 5],
            'Brigadeiro': [5, 5, 5, 5, 4],
            'Beijinho': [4, 5, 4, 5, 5],
            'Docinho de Coco': [4, 4, 5, 4, 4],
        }
        
        # Atualizar categorias
        for nome, categoria in categorias_map.items():
            bolos = Bolo.objects.filter(sabor=nome)
            for bolo in bolos:
                if bolo.categoria != categoria:
                    self.stdout.write(
                        f'  Atualizando {bolo.sabor}: {bolo.categoria} → {categoria}'
                    )
                    bolo.categoria = categoria
                    bolo.save()
        
        # Adicionar avaliações
        for nome, notas in avaliacoes_map.items():
            bolos = Bolo.objects.filter(sabor=nome)
            for bolo in bolos:
                # Remover avaliações antigas
                Avaliacao.objects.filter(produto=bolo).delete()
                
                # Adicionar novas avaliações
                for nota in notas:
                    Avaliacao.objects.create(
                        produto=bolo,
                        nota=nota,
                        comentario='Testando o sistema'
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {bolo.sabor}: {len(notas)} avaliações adicionadas')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\nCategorias e avaliações atualizadas com sucesso!')
        )
