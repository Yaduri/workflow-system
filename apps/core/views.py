from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from apps.core.models import TipoProcesso, Fase, CampoFormulario
from apps.formularios.models import FormularioExterno
from apps.usuarios.models import PerfilUsuario
from django.contrib.auth.models import User


@staff_member_required
def configuracoes_index(request):
    """Dashboard de configurações"""
    stats = {
        'tipos_processo': TipoProcesso.objects.count(),
        'fases': Fase.objects.count(),
        'campos': CampoFormulario.objects.count(),
        'formularios_externos': FormularioExterno.objects.count(),
        'usuarios': User.objects.count(),
    }
    
    return render(request, 'configuracoes/index.html', {'stats': stats})


@staff_member_required
def tipos_processo_lista(request):
    """Lista tipos de processo"""
    tipos = TipoProcesso.objects.all().order_by('nome')
    return render(request, 'configuracoes/tipos_processo/lista.html', {'tipos': tipos})


@staff_member_required
def tipos_processo_criar(request):
    """Cria novo tipo de processo"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        prefixo = request.POST.get('prefixo_numero')
        ativo = request.POST.get('ativo') == 'on'
        
        try:
            TipoProcesso.objects.create(
                nome=nome,
                descricao=descricao,
                prefixo_numero=prefixo,
                ativo=ativo
            )
            messages.success(request, f'Tipo de processo "{nome}" criado com sucesso!')
            return redirect('configuracoes:tipos_processo_lista')
        except Exception as e:
            messages.error(request, f'Erro ao criar tipo de processo: {str(e)}')
    
    return render(request, 'configuracoes/tipos_processo/form.html')


@staff_member_required
def tipos_processo_editar(request, tipo_id):
    """Edita tipo de processo"""
    tipo = get_object_or_404(TipoProcesso, id=tipo_id)
    
    if request.method == 'POST':
        tipo.nome = request.POST.get('nome')
        tipo.descricao = request.POST.get('descricao')
        tipo.prefixo_numero = request.POST.get('prefixo_numero')
        tipo.ativo = request.POST.get('ativo') == 'on'
        
        try:
            tipo.save()
            messages.success(request, f'Tipo de processo "{tipo.nome}" atualizado com sucesso!')
            return redirect('configuracoes:tipos_processo_lista')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar tipo de processo: {str(e)}')
    
    return render(request, 'configuracoes/tipos_processo/form.html', {'tipo': tipo})


@staff_member_required
def fases_gerenciar(request, tipo_id):
    """Gerencia fases de um tipo de processo"""
    tipo = get_object_or_404(TipoProcesso, id=tipo_id)
    fases = tipo.fases.all().order_by('ordem')
    
    if request.method == 'POST':
        # Adicionar nova fase
        nome = request.POST.get('nome')
        ordem = request.POST.get('ordem')
        setor = request.POST.get('setor_responsavel')
        cor = request.POST.get('cor_badge', '#6c757d')
        fase_inicial = request.POST.get('fase_inicial') == 'on'
        fase_final = request.POST.get('fase_final') == 'on'
        
        try:
            Fase.objects.create(
                tipo_processo=tipo,
                nome=nome,
                ordem=ordem,
                setor_responsavel=setor,
                cor_badge=cor,
                fase_inicial=fase_inicial,
                fase_final=fase_final,
                permite_avancar=True,
                permite_retornar=True
            )
            messages.success(request, f'Fase "{nome}" adicionada com sucesso!')
            return redirect('configuracoes:fases_gerenciar', tipo_id=tipo_id)
        except Exception as e:
            messages.error(request, f'Erro ao adicionar fase: {str(e)}')
    
    return render(request, 'configuracoes/fases/gerenciar.html', {
        'tipo': tipo,
        'fases': fases
    })


@staff_member_required
def campos_gerenciar(request, tipo_id):
    """Gerencia campos de um tipo de processo"""
    tipo = get_object_or_404(TipoProcesso, id=tipo_id)
    campos = tipo.campos.all().order_by('grupo', 'ordem')
    
    if request.method == 'POST':
        # Adicionar novo campo
        nome_campo = request.POST.get('nome_campo')
        label = request.POST.get('label')
        tipo_campo = request.POST.get('tipo_campo')
        grupo = request.POST.get('grupo', '')
        ordem = request.POST.get('ordem', 0)
        obrigatorio = request.POST.get('obrigatorio') == 'on'
        visivel_externo = request.POST.get('visivel_formulario_externo') == 'on'
        placeholder = request.POST.get('placeholder', '')
        ajuda = request.POST.get('ajuda', '')
        
        try:
            CampoFormulario.objects.create(
                tipo_processo=tipo,
                nome_campo=nome_campo,
                label=label,
                tipo_campo=tipo_campo,
                grupo=grupo,
                ordem=ordem,
                obrigatorio=obrigatorio,
                visivel_formulario_externo=visivel_externo,
                placeholder=placeholder,
                ajuda=ajuda
            )
            messages.success(request, f'Campo "{label}" adicionado com sucesso!')
            return redirect('configuracoes:campos_gerenciar', tipo_id=tipo_id)
        except Exception as e:
            messages.error(request, f'Erro ao adicionar campo: {str(e)}')
    
    return render(request, 'configuracoes/campos/gerenciar.html', {
        'tipo': tipo,
        'campos': campos
    })


@staff_member_required
def formularios_externos_lista(request):
    """Lista formulários externos"""
    formularios = FormularioExterno.objects.select_related('tipo_processo').all()
    return render(request, 'configuracoes/formularios/lista.html', {
        'formularios': formularios
    })


@staff_member_required
def formularios_externos_criar(request):
    """Cria formulário externo"""
    tipos = TipoProcesso.objects.filter(ativo=True)
    
    if request.method == 'POST':
        tipo_id = request.POST.get('tipo_processo')
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        mensagem_sucesso = request.POST.get('mensagem_sucesso')
        cor_tema = request.POST.get('cor_tema', '#2D5BFF')
        ativo = request.POST.get('ativo') == 'on'
        
        try:
            tipo = TipoProcesso.objects.get(id=tipo_id)
            formulario = FormularioExterno.objects.create(
                tipo_processo=tipo,
                titulo=titulo,
                descricao=descricao,
                mensagem_sucesso=mensagem_sucesso,
                cor_tema=cor_tema,
                ativo=ativo
            )
            messages.success(request, f'Formulário externo criado! Link: /formulario/{formulario.token}/')
            return redirect('configuracoes:formularios_externos_lista')
        except Exception as e:
            messages.error(request, f'Erro ao criar formulário: {str(e)}')
    
    return render(request, 'configuracoes/formularios/form.html', {'tipos': tipos})


@staff_member_required
def usuarios_lista(request):
    """Lista usuários"""
    usuarios = User.objects.select_related('perfilusuario').all().order_by('username')
    return render(request, 'configuracoes/usuarios/lista.html', {
        'usuarios': usuarios
    })


@staff_member_required
def usuarios_criar(request):
    """Cria novo usuário"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        setor = request.POST.get('setor')
        telefone = request.POST.get('telefone', '')
        is_staff = request.POST.get('is_staff') == 'on'
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_staff=is_staff
                )
                PerfilUsuario.objects.create(
                    user=user,
                    setor=setor,
                    telefone=telefone,
                    ativo=True
                )
            messages.success(request, f'Usuário "{username}" criado com sucesso!')
            return redirect('configuracoes:usuarios_lista')
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
    
    return render(request, 'configuracoes/usuarios/form.html')
