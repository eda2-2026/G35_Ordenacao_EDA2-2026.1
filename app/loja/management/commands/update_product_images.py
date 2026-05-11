from django.core.management.base import BaseCommand
from loja.models import Bolo
import random

class Command(BaseCommand):
    help = 'Atualiza as imagens dos produtos com URLs de imagens reais'

    def handle(self, *args, **options):
        # URLs de imagens de alta qualidade do Pexels (todas funcionam)
        imagens_por_sabor = {
            'Chocolate': [
                'https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg?auto=compress&cs=tinysrgb&w=600',
                'https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600',
                'https://images.pexels.com/photos/1092730/pexels-photo-1092730.jpeg?auto=compress&cs=tinysrgb&w=600',
            ],
            'Morango': [
                'https://images.pexels.com/photos/1556508/pexels-photo-1556508.jpeg?auto=compress&cs=tinysrgb&w=600',
                'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=600',
            ],
            'Baunilha': [
                'https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg?auto=compress&cs=tinysrgb&w=600',
                'https://images.pexels.com/photos/3407666/pexels-photo-3407666.jpeg?auto=compress&cs=tinysrgb&w=600',
            ],
            'Brigadeiro': [
                'https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600',
                'https://images.pexels.com/photos/1092730/pexels-photo-1092730.jpeg?auto=compress&cs=tinysrgb&w=600',
            ],
            'Cenoura': [
                'https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg?auto=compress&cs=tinysrgb&w=600',
                'https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600',
            ],
            'Frutas': [
                'https://images.pexels.com/photos/1556508/pexels-photo-1556508.jpeg?auto=compress&cs=tinysrgb&w=600',
                'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=600',
            ],
            'Caramelo': [
                'https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600',
            ],
        }

        def mapear_sabor_para_categoria(sabor_nome):
            """Mapeia o nome do bolo para uma categoria de imagem"""
            sabor_lower = sabor_nome.lower()
            
            # Verificar palavras-chave específicas
            if 'chocolate' in sabor_lower or 'brownie' in sabor_lower:
                return 'Chocolate'
            elif 'morango' in sabor_lower or 'frutas vermelhas' in sabor_lower:
                return 'Morango'
            elif 'baunilha' in sabor_lower:
                return 'Baunilha'
            elif 'brigadeiro' in sabor_lower:
                return 'Brigadeiro'
            elif 'cenoura' in sabor_lower:
                return 'Cenoura'
            elif any(x in sabor_lower for x in ['banana', 'abacaxi', 'pêssego', 'frutas', 'limão']):
                return 'Frutas'
            elif any(x in sabor_lower for x in ['doce de leite', 'ninho', 'churros', 'caramelo', 'toffee']):
                return 'Caramelo'
            elif 'red velvet' in sabor_lower:
                return 'Chocolate'
            elif 'fubá' in sabor_lower or 'milho' in sabor_lower:
                return 'Baunilha'
            elif 'coco' in sabor_lower:
                return 'Baunilha'
            else:
                return random.choice(list(imagens_por_sabor.keys()))

        atualizado = 0
        for bolo in Bolo.objects.all():
            # Mapear o sabor para categoria de imagem
            categoria = mapear_sabor_para_categoria(bolo.sabor)
            
            # Selecionar imagem aleatória da categoria
            if categoria in imagens_por_sabor:
                urls = imagens_por_sabor[categoria]
                nova_url = random.choice(urls)
                bolo.imagem_url = nova_url
                bolo.save()
                atualizado += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {bolo.sabor} ({categoria}) - URL atualizada')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n{atualizado} imagens atualizadas com sucesso!')
        )
