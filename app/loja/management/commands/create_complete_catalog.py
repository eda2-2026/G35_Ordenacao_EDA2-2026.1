from django.core.management.base import BaseCommand
from loja.models import Bolo, Avaliacao
from decimal import Decimal

class Command(BaseCommand):
    help = 'Cria produtos em todas as categorias com diferentes sabores e tamanhos'

    def handle(self, *args, **options):
        # Estrutura: categoria -> sabores
        produtos = {
            'Bolos': [
                'Bolo de Chocolate',
                'Bolo de Morango',
                'Bolo de Baunilha',
                'Bolo de Brigadeiro',
                'Bolo de Cenoura',
            ],
            'Doces': [
                'Docinho de Chocolate',
                'Docinho de Morango',
                'Docinho de Baunilha',
                'Docinho de Brigadeiro',
                'Docinho de Cenoura',
            ],
            'Cupcakes': [
                'Cupcake de Chocolate',
                'Cupcake de Morango',
                'Cupcake de Baunilha',
                'Cupcake de Brigadeiro',
                'Cupcake de Cenoura',
            ],
            'Outros': [
                'Brownie de Chocolate',
                'Brownie de Morango',
                'Brownie de Baunilha',
                'Brownie de Brigadeiro',
                'Brownie de Cenoura',
            ],
        }
        
        tamanhos = ['P', 'M', 'G']
        precos_base = {'P': 15.00, 'M': 25.00, 'G': 35.00}
        
        criados = 0
        for categoria, sabores in produtos.items():
            for sabor in sabores:
                for tamanho in tamanhos:
                    # Verificar se já existe
                    exists = Bolo.objects.filter(
                        sabor=sabor,
                        categoria=categoria,
                        tamanho_padrao=tamanho
                    ).exists()
                    
                    if exists:
                        self.stdout.write(f'  (j\u00e1 existe) {sabor} - {tamanho}')
                        continue
                    
                    # Criar o bolo
                    preco = Decimal(str(precos_base[tamanho]))
                    bolo = Bolo.objects.create(
                        sabor=sabor,
                        categoria=categoria,
                        tamanho_padrao=tamanho,
                        preco_pequeno=preco if tamanho == 'P' else Decimal('15.00'),
                        preco_medio=preco if tamanho == 'M' else Decimal('25.00'),
                        preco_grande=preco if tamanho == 'G' else Decimal('35.00'),
                        imagem_url=f'https://via.placeholder.com/250x250?text={sabor.replace(" ", "+")}',
                    )
                    
                    # Adicionar avaliações aleat\u00f3rias
                    notas = [3, 4, 4, 5, 5] if 'Chocolate' in sabor else [4, 4, 5, 5, 3]
                    for nota in notas:
                        Avaliacao.objects.create(
                            produto=bolo,
                            nota=nota,
                            comentario='Testando sistema de filtros'
                        )
                    
                    # Adicionar algumas vendas aleat\u00f3rias
                    from loja.models import Order, OrderItem
                    from django.contrib.auth.models import User
                    user, _ = User.objects.get_or_create(username='test_vendor')
                    
                    vendas = 5 if 'Chocolate' in sabor else 3
                    for _ in range(vendas):
                        order = Order.objects.create(user=user, status='completed')
                        OrderItem.objects.create(
                            order=order,
                            bolo=bolo,
                            tamanho=tamanho,
                            preco=preco,
                            quantidade=1
                        )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {bolo.sabor} ({categoria}) - {tamanho}')
                    )
                    criados += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{criados} produtos criados com sucesso!')
        )
