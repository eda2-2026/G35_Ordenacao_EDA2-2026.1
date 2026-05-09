from django.contrib import admin
from django import forms
from .models import Bolo, Avaliacao
from .models import Order, OrderItem


class BoloAdminForm(forms.ModelForm):
    preco_override = forms.DecimalField(max_digits=6, decimal_places=2, required=False)

    class Meta:
        model = Bolo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializa preco_override com o preço do tamanho padrão quando houver instancia
        if getattr(self, 'instance', None) and self.instance.pk:
            tp = getattr(self.instance, 'tamanho_padrao', 'P')
            preco_val = self.instance.get_preco_por_tamanho(tp) or self.instance.preco_pequeno
            self.fields['preco_override'].initial = preco_val


@admin.register(Bolo)
class BoloAdmin(admin.ModelAdmin):
    form = BoloAdminForm
    # Mostrar sabor, categoria, tamanho padrão e um preço editável no form/list
    list_display = ('sabor', 'categoria', 'tamanho_padrao', 'preco_display')
    list_editable = ('categoria', 'tamanho_padrao')
    search_fields = ('sabor', 'categoria')
    fields = ('sabor', 'categoria', 'tamanho_padrao', 'preco_override', 'descricao', 'imagem_url')

    def save_model(self, request, obj, form, change):
        preco = form.cleaned_data.get('preco_override') if form.is_valid() else None
        if preco is not None:
            tp = getattr(obj, 'tamanho_padrao', 'P')
            if tp == 'P':
                obj.preco_pequeno = preco
            elif tp == 'M':
                obj.preco_medio = preco
            elif tp == 'G':
                obj.preco_grande = preco
        super().save_model(request, obj, form, change)

    def preco_display(self, obj):
        v = obj.get_preco_por_tamanho(getattr(obj, 'tamanho_padrao', 'P')) or obj.preco_pequeno
        return f"R$ {v:.2f}"
    preco_display.short_description = 'Preço'


admin.site.register(Order)
admin.site.register(OrderItem)
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'nota', 'data_criacao')
    list_filter = ('nota', 'data_criacao')
    search_fields = ('produto__sabor', 'comentario')
