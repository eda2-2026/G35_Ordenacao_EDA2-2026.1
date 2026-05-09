from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, logout as logout_view, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .models import Bolo, Profile, Order, OrderItem, Avaliacao
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from .trie_store import get_trie
import json
from django.db.models import Sum
from .sort_engine.radix_sort import RadixSort
from .sort_engine.quick_sort import QuickSort


@login_required
def home(request):
    return render(request, 'home.html')


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Nome de usuário ou senha incorretos")

    return render(request, 'login.html')


def logout(request):
    logout_view(request)
    return redirect('login')


def cadastro(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Usuário já existe")
            else:
                user = User.objects.create_user(
                    username=username, password=password)
                user.save()
                messages.success(request, "Usuário cadastrado com sucesso")
                return redirect('login')
        else:
            messages.error(request, "As senhas não coincidem")
    return render(request, 'cadastro.html')


@login_required
def catalogo(request):
    bolos = Bolo.objects.all()  # Busca todos os bolos do banco de dados
    return render(request, 'catalogo.html', {'bolos': bolos})


def api_catalogo(request):
    """API que retorna produtos com filtros aplicáveis via query params.

    Aceita query params:
      - categoria (ex: 'Bolos')
      - tamanho (ex: 'P', 'M', 'G' ou 'Pequeno')
      - sabor (string ou CSV)
      - avaliacao (inteiro mínimo da média de avaliações)
      - sort (az|za|menor_preco|maior_preco)

    Retorna lista JSON com campos: id, nome, categoria, tamanho, preco, media_notas, vendas, imagem_url
    """
    qs = Bolo.objects.all()
    # Anotar média de notas e total de vendas
    from django.db.models import Avg, Count
    qs = qs.annotate(media_notas=Avg('avaliacoes__nota'), vendas=Sum('orderitem__quantidade'))

    # Aplicar filtros recebidos
    categoria = request.GET.get('categoria') or request.GET.get('categories')
    tamanho = request.GET.get('tamanho') or request.GET.get('sizes')
    sabor_q = request.GET.get('sabor') or request.GET.get('sabores')
    min_avaliacao = request.GET.get('avaliacao') or request.GET.get('min_rating')

    if categoria:
        
        mapping = {
            'bolo': 'Bolos',
            'bolos': 'Bolos',
            'docinho': 'Doces',
            'docinhos': 'Doces',
            'doce': 'Doces',
            'doces': 'Doces',
            'cupcake': 'Cupcakes',
            'cupcakes': 'Cupcakes',
            'bolo no pote': 'Bolos no Pote',
            'bolos no pote': 'Bolos no Pote',
            'pote': 'Bolos no Pote',
            'brownie': 'Outros',
            'outros': 'Outros',
        }
        raw = [c.strip() for c in categoria.split(',') if c.strip()]
        mapped = []
        for r in raw:
            key = r.strip().lower()
            if key in mapping:
                mapped.append(mapping[key])
            else:
                title = r.strip().title()
                mapped.append(title)

        qs = qs.filter(categoria__in=mapped)

    if tamanho:
        sizes = [s.strip() for s in tamanho.split(',') if s.strip()]
        # normalizar nomes para a sigla quando possível
        norm = []
        for s in sizes:
            s_low = s.lower()
            if s_low.startswith('p'):
                norm.append('P')
            elif s_low.startswith('m'):
                norm.append('M')
            elif s_low.startswith('g'):
                norm.append('G')
        if norm:
            qs = qs.filter(tamanho_padrao__in=norm)

    if sabor_q:
        sabores = [s.strip() for s in sabor_q.split(',') if s.strip()]
        
        from django.db.models import Q
        q_sabor = Q()
        for s in sabores:
            q_sabor |= Q(sabor__icontains=s)
        qs = qs.filter(q_sabor)

    if min_avaliacao:
        try:
            mr = float(min_avaliacao)
            qs = qs.filter(media_notas__gte=mr)
        except Exception:
            pass

    sort = request.GET.get('sort', '').lower()

    resultado = []
    for b in qs:
        try:
            preco_val = b.get_preco_por_tamanho(getattr(b, 'tamanho_padrao', 'P'))
            if preco_val is None:
                preco_val = b.preco_pequeno
            preco = float(preco_val)
        except Exception:
            preco = float(b.preco_pequeno)

        resultado.append({
            'id': b.id,
            'nome': b.sabor,
            'categoria': b.categoria,
            'tamanho': getattr(b, 'tamanho_padrao', 'P'),
            'preco': preco,
            'media_notas': float(b.media_notas) if b.media_notas is not None else None,
            'vendas': int(b.vendas or 0),
            'imagem_url': b.imagem_url,
        })

    # Ordenação usando os algoritmos do motor de ordenação 
    if sort == 'az':
        resultado = QuickSort().ordenar(resultado, 'nome')
    elif sort == 'za':
        resultado = QuickSort().ordenar(resultado, 'nome', reverse=True)
    elif sort == 'menor_preco':
        resultado = RadixSort().ordenar(resultado, 'preco')
    elif sort == 'maior_preco':
        resultado = RadixSort().ordenar(resultado, 'preco', reverse=True)
    else:
        # relevância: por vendas desc, depois media_notas desc
        resultado.sort(key=lambda x: (x.get('vendas', 0) or 0, x.get('media_notas', 0) or 0), reverse=True)

    return JsonResponse(resultado, safe=False)


@require_POST
def criar_avaliacao(request):
   
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'invalid_json'}, status=400)

    produto_id = payload.get('produto_id') or payload.get('bolo_id')
    nota = payload.get('nota')
    comentario = payload.get('comentario', '')

    if not produto_id or not nota:
        return JsonResponse({'success': False, 'error': 'missing_fields'}, status=400)

    try:
        produto = Bolo.objects.get(id=produto_id)
    except Bolo.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'produto_not_found'}, status=404)

    try:
        nota_int = int(nota)
        if nota_int < 1 or nota_int > 5:
            raise ValueError()
    except Exception:
        return JsonResponse({'success': False, 'error': 'invalid_nota'}, status=400)

    aval = Avaliacao.objects.create(produto=produto, nota=nota_int, comentario=comentario)
    # recalcular média
    from django.db.models import Avg
    media = Avaliacao.objects.filter(produto=produto).aggregate(avg=Avg('nota'))['avg']
    media = float(media) if media is not None else None

    return JsonResponse({'success': True, 'avaliacao_id': aval.id, 'media_notas': media})


@login_required
def basket(request):
    profile = Profile.objects.get(user=request.user)
    carrinho = profile.listar_carrinho()
    total = profile.obter_valor_total()
    return render(request, 'basket.html', {'carrinho': carrinho, 'total': total})


@login_required
def admin(request):
    return render(request, 'admin.html')


@require_POST
def adicionar_ao_carrinho(request):
    """Adiciona um bolo ao carrinho.

    Suporta usuários autenticados (salva no Profile.carrinho) e
    usuários anônimos (salva no session['cart']). Retorna JSON.
    """
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'invalid_payload'}, status=400)

    bolo_id = data.get('bolo_id')
    tamanho = (data.get('tamanho') or 'P').upper()

    bolo = get_object_or_404(Bolo, id=bolo_id)

    
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        profile.adicionar_bolo_ao_carrinho(bolo, tamanho)
        return JsonResponse({'success': True})

    
    cart = request.session.get('cart', [])
    preco = float(bolo.get_preco_por_tamanho(tamanho) or bolo.preco_pequeno)
    found = False
    for item in cart:
        if item.get('bolo_id') == bolo.id and item.get('tamanho') == tamanho:
            item['quantidade'] = int(item.get('quantidade', 1)) + 1
            found = True
            break
    if not found:
        cart.append({'bolo_id': bolo.id, 'tamanho': tamanho, 'preco': preco, 'quantidade': 1})

    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'success': True})


def obter_carrinho(request):
    """Retorna o carrinho atual. Se o usuário estiver autenticado, lê do Profile;
    caso contrário, lê do `request.session['cart']`.
    """
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        carrinho = []
        for item in profile.listar_carrinho():
            bolo = Bolo.objects.get(id=item['bolo_id'])
            carrinho.append({
                'bolo_id': bolo.id,
                'bolo_nome': bolo.sabor,
                'descricao': bolo.descricao,
                'imagem_url': bolo.imagem_url,
                'tamanho': item['tamanho'],
                'preco': item['preco'],
                'quantidade': item['quantidade']
            })
        total = profile.obter_valor_total()
        return JsonResponse({'carrinho': carrinho, 'total': str(total)})

   
    session_cart = request.session.get('cart', [])
    carrinho = []
    total = 0.0
    for item in session_cart:
        try:
            bolo = Bolo.objects.get(id=item.get('bolo_id'))
        except Bolo.DoesNotExist:
            continue
        quantidade = int(item.get('quantidade', 1))
        preco = float(item.get('preco', 0))
        total += preco * quantidade
        carrinho.append({
            'bolo_id': bolo.id,
            'bolo_nome': bolo.sabor,
            'descricao': bolo.descricao,
            'imagem_url': bolo.imagem_url,
            'tamanho': item.get('tamanho'),
            'preco': preco,
            'quantidade': quantidade
        })

    return JsonResponse({'carrinho': carrinho, 'total': str(total)})


def listar_carrinho(request):
    profile = Profile.objects.get(user=request.user)
    return JsonResponse({'carrinho': profile.listar_carrinho()})


@require_POST
def remover_do_carrinho(request):
    """Remove (ou decrementa) um item do carrinho.

    Aceita JSON: {"bolo_id": <id>, "tamanho": "P|M|G"}
    Suporta usuário autenticado (Profile) e anônimo (session['cart']).
    """
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'invalid_payload'}, status=400)

    bolo_id = data.get('bolo_id')
    tamanho = (data.get('tamanho') or 'P').upper()

    if not bolo_id:
        return JsonResponse({'success': False, 'error': 'missing_bolo_id'}, status=400)

    # Usuário autenticado
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        changed = False
        for idx, item in enumerate(list(profile.carrinho)):
            if int(item.get('bolo_id')) == int(bolo_id) and item.get('tamanho') == tamanho:
                # decrementa quantidade ou remove
                quantidade = int(item.get('quantidade', 1))
                preco = Decimal(str(item.get('preco', 0)))
                if quantidade > 1:
                    profile.carrinho[idx]['quantidade'] = quantidade - 1
                    profile.valor_total_carrinho = max(Decimal('0.00'), profile.valor_total_carrinho - preco)
                else:
                    # remove item
                    profile.carrinho.pop(idx)
                    profile.valor_total_carrinho = max(Decimal('0.00'), profile.valor_total_carrinho - preco)
                changed = True
                break

        if changed:
            profile.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'item_not_found'}, status=404)

    
    session_cart = request.session.get('cart', [])
    changed = False
    for idx, item in enumerate(list(session_cart)):
        if int(item.get('bolo_id')) == int(bolo_id) and item.get('tamanho') == tamanho:
            quantidade = int(item.get('quantidade', 1))
            if quantidade > 1:
                session_cart[idx]['quantidade'] = quantidade - 1
            else:
                session_cart.pop(idx)
            changed = True
            break

    if changed:
        request.session['cart'] = session_cart
        request.session.modified = True
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'item_not_found'}, status=404)


@login_required
def finalizar_compra(request):
    profile = request.user.profile
    carrinho = profile.listar_carrinho()

    if not carrinho:
        return JsonResponse({'success': False, 'error': 'Carrinho vazio'})

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user, total=Decimal('0.00'), status='COMPLETED')
        total = Decimal('0.00')
        for item in carrinho:
            bolo = Bolo.objects.get(id=item['bolo_id'])
            preco = Decimal(str(item.get('preco', 0)))
            quantidade = int(item.get('quantidade', 1))
            OrderItem.objects.create(
                order=order, bolo=bolo, tamanho=item['tamanho'], preco=preco, quantidade=quantidade)
            total += preco * quantidade

        order.total = total
        order.save()

        profile.limpar_carrinho()

    return JsonResponse({'success': True, 'order_id': order.id})


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        user = request.user
        novo_nome = request.POST.get('name')
        nova_senha = request.POST.get('newPassword')

        if novo_nome:
            user.username = novo_nome

        if nova_senha:
            user.set_password(nova_senha)

        user.save()

        logout(request)

        messages.success(
            request, 'Seu perfil foi atualizado com sucesso. Por favor, faça login com suas novas credenciais.')

        return redirect('login')

    return render(request, 'editar_perfil.html')


@login_required
def deletar_perfil(request):
    if request.method == 'POST':
        user = request.user
        user.delete()

        messages.success(request, 'Perfil excluído com sucesso!')
        return redirect('cadastro')

    return redirect('adm')


@login_required
@require_GET
def autocomplete(request):
    
    prefix = request.GET.get('q', '').strip()
    if not prefix:
        return JsonResponse({'suggestions': []})

    trie = get_trie()
    resultados = trie.starts_with(prefix, limit=8)

    sugestoes = []
    for item in resultados:
        if isinstance(item, dict):
            label = item.get('label') or item.get(
                'nome') or item.get('sabor') or str(item)
        else:
            label = str(item)
        if label and label not in sugestoes:
            sugestoes.append(label)

    return JsonResponse({'suggestions': sugestoes})
