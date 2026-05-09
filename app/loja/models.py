from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


class Bolo(models.Model):
    TAMANHOS = [
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
    ]

    sabor = models.CharField(max_length=100)
    descricao = models.TextField()
    imagem_url = models.URLField()
    CATEGORIAS = [
        ('Bolos', 'Bolos'),
        ('Cupcakes', 'Cupcakes'),
        ('Doces', 'Doces'),
        ('Bolos no Pote', 'Bolos no Pote'),
        ('Outros', 'Outros'),
    ]
    categoria = models.CharField(max_length=32, choices=CATEGORIAS, default='Doces')
    
    # Preços para cada tamanho
    preco_pequeno = models.DecimalField(max_digits=6, decimal_places=2, default=15.00)
    preco_medio = models.DecimalField(max_digits=6, decimal_places=2, default=25.00)
    preco_grande = models.DecimalField(max_digits=6, decimal_places=2, default=35.00)

    # Tamanho padrão do produto 
    tamanho_padrao = models.CharField(max_length=1, choices=TAMANHOS, default='P')
    avaliacao = models.IntegerField(default=5)

    def get_preco_por_tamanho(self, tamanho):
        if tamanho == 'P':
            return self.preco_pequeno
        elif tamanho == 'M':
            return self.preco_medio
        elif tamanho == 'G':
            return self.preco_grande
        else:
            return None

    def __str__(self):
        return self.sabor


class Avaliacao(models.Model):
    produto = models.ForeignKey(Bolo, on_delete=models.CASCADE, related_name='avaliacoes')
    nota = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Avaliacao {self.nota} - {self.produto.sabor}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    carrinho = models.JSONField(default=list)  # Carrinho como lista de dicionários
    valor_total_carrinho = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username

    def adicionar_bolo_ao_carrinho(self, bolo, tamanho):
        
        preco = bolo.get_preco_por_tamanho(tamanho)
        if preco is None:
            raise ValueError("Tamanho inválido")

        # Converte o preço de Decimal para float
        preco = float(preco)

        # Verifica se o bolo de tamanho específico já está no carrinho
        for item in self.carrinho:
            if item['bolo_id'] == bolo.id and item['tamanho'] == tamanho:
                
                item['quantidade'] += 1
               
                self.valor_total_carrinho += Decimal(preco)
                break
        else:
 
            self.carrinho.append({'bolo_id': bolo.id, 'tamanho': tamanho, 'preco': preco, 'quantidade': 1})
            
            self.valor_total_carrinho += Decimal(preco)

        # Salva o perfil com o carrinho atualizado e o valor total
        self.save()

    def listar_carrinho(self):
        return self.carrinho

    def obter_valor_total(self):
        return self.valor_total_carrinho
    
    def limpar_carrinho(self):
        # Limpa o carrinho e zera o valor total
        self.carrinho = []
        self.valor_total_carrinho = 0.00
        self.save()


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('COMPLETED', 'Concluído'),
        ('CANCELLED', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username} - {self.status}"


class OrderItem(models.Model):
    TAMANHOS = [
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    bolo = models.ForeignKey(Bolo, on_delete=models.PROTECT)
    tamanho = models.CharField(max_length=1, choices=TAMANHOS)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.bolo.sabor} x{self.quantidade} ({self.tamanho})"



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
