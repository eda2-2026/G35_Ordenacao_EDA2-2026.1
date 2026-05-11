from django.core.management.base import BaseCommand
from loja.models import Bolo, OrderItem, Order
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Adiciona vendas fictícias aos produtos para testar HeapSort'

    def handle(self, *args, **options):
        # Obter ou criar um usuário fictício para os pedidos
        user, _ = User.objects.get_or_create(username='test_vendor', defaults={'first_name': 'Test'})
        
        bolos = Bolo.objects.all()[:10]
        vendas_map = {
            0: 150,  # 1º mais vendido
            1: 120,
            2: 95,
            3: 87,
            4: 72,
            5: 65,
            6: 48,
            7: 35,
            8: 22,
            9: 10,
        }

        for idx, bolo in enumerate(bolos):
            # Remove vendas antigas para este bolo
            OrderItem.objects.filter(bolo=bolo).delete()
            
            # Cria novas vendas
            quantidade = vendas_map.get(idx, 5)
            
            # Cria um Order fictício para cada 5 itens
            items_criados = 0
            for i in range(quantidade):
                if i % 5 == 0:
                    order = Order.objects.create(user=user, status='completed')
                
                OrderItem.objects.create(
                    order=order,
                    bolo=bolo,
                    tamanho='P',
                    preco=bolo.preco_pequeno,
                    quantidade=1
                )
                items_criados += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ {bolo.sabor}: {quantidade} vendas')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Vendas fictícias adicionadas com sucesso!')
        )
