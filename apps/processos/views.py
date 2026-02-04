from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import InstanciaProcesso
from apps.core.models import TipoProcesso, Fase
from apps.workflow.services import WorkflowService
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
def lista_processos(request):
    """Lista todos os processos com filtros"""
    processos = InstanciaProcesso.objects.select_related(
        'tipo_processo', 'fase_atual', 'responsavel_atual', 'criado_por'
    ).all()
    
    # Filtros
    tipo_id = request.GET.get('tipo')
    fase_id = request.GET.get('fase')
    setor = request.GET.get('setor')
    responsavel_id = request.GET.get('responsavel')
    busca = request.GET.get('busca')
    
    if tipo_id:
        processos = processos.filter(tipo_processo_id=tipo_id)
    
    if fase_id:
        processos = processos.filter(fase_atual_id=fase_id)
    
    if setor:
        processos = processos.filter(fase_atual__setor_responsavel=setor)
    
    if responsavel_id:
        processos = processos.filter(responsavel_atual_id=responsavel_id)
    
    if busca:
        processos = processos.filter(
            Q(numero__icontains=busca) |
            Q(dados__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(processos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    tipos_processo = TipoProcesso.objects.filter(ativo=True)
    fases = Fase.objects.all()
    
    # Estatísticas
    stats = {
        'total': processos.count(),
        'por_fase': processos.values('fase_atual__nome').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
    }
    
    context = {
        'page_obj': page_obj,
        'tipos_processo': tipos_processo,
        'fases': fases,
        'stats': stats,
        'filtros': {
            'tipo': tipo_id,
            'fase': fase_id,
            'setor': setor,
            'responsavel': responsavel_id,
            'busca': busca,
        }
    }
    
    return render(request, 'processos/lista.html', context)


@login_required
def detalhes_processo(request, processo_id):
    """Exibe detalhes completos de um processo"""
    processo = get_object_or_404(
        InstanciaProcesso.objects.select_related(
            'tipo_processo', 'fase_atual', 'responsavel_atual', 'criado_por'
        ),
        id=processo_id
    )
    
    # Verifica permissão de acesso
    if not processo._usuario_tem_permissao_fase(request.user, processo.fase_atual):
        if not request.user.is_superuser:
            messages.error(request, 'Você não tem permissão para acessar este processo.')
            return redirect('processos:lista')
    
    # Histórico
    historico = processo.historico.select_related(
        'usuario', 'fase_anterior', 'fase_nova'
    ).all()
    
    # Fases disponíveis para transição
    fases_disponiveis = processo.get_fases_disponiveis(request.user)
    
    # Dados formatados
    dados_formatados = processo.get_dados_formatados()
    
    context = {
        'processo': processo,
        'historico': historico,
        'fases_disponiveis': fases_disponiveis,
        'dados_formatados': dados_formatados,
    }
    
    return render(request, 'processos/detalhes.html', context)


@login_required
@require_POST
def mudar_fase(request, processo_id):
    """Muda a fase de um processo"""
    processo = get_object_or_404(InstanciaProcesso, id=processo_id)
    nova_fase_id = request.POST.get('nova_fase')
    observacoes = request.POST.get('observacoes', '')
    
    if not nova_fase_id:
        messages.error(request, 'Selecione uma fase.')
        return redirect('processos:detalhes', processo_id=processo_id)
    
    nova_fase = get_object_or_404(Fase, id=nova_fase_id)
    
    # Usa o serviço de workflow
    sucesso, mensagem = WorkflowService.transicionar_fase(
        instancia=processo,
        nova_fase=nova_fase,
        usuario=request.user,
        observacoes=observacoes
    )
    
    if sucesso:
        messages.success(request, mensagem)
    else:
        messages.error(request, mensagem)
    
    return redirect('processos:detalhes', processo_id=processo_id)


@login_required
@require_POST
def atribuir_responsavel(request, processo_id):
    """Atribui um responsável ao processo"""
    from django.contrib.auth.models import User
    
    processo = get_object_or_404(InstanciaProcesso, id=processo_id)
    responsavel_id = request.POST.get('responsavel')
    observacoes = request.POST.get('observacoes', '')
    
    if not responsavel_id:
        messages.error(request, 'Selecione um responsável.')
        return redirect('processos:detalhes', processo_id=processo_id)
    
    novo_responsavel = get_object_or_404(User, id=responsavel_id)
    
    sucesso, mensagem = WorkflowService.atribuir_responsavel(
        instancia=processo,
        novo_responsavel=novo_responsavel,
        usuario_que_atribuiu=request.user,
        observacoes=observacoes
    )
    
    if sucesso:
        messages.success(request, mensagem)
    else:
        messages.error(request, mensagem)
    
    return redirect('processos:detalhes', processo_id=processo_id)


@login_required
@require_POST
def adicionar_comentario(request, processo_id):
    """Adiciona um comentário ao processo"""
    processo = get_object_or_404(InstanciaProcesso, id=processo_id)
    comentario = request.POST.get('comentario', '')
    
    sucesso, mensagem = WorkflowService.adicionar_comentario(
        instancia=processo,
        usuario=request.user,
        comentario=comentario
    )
    
    if sucesso:
        messages.success(request, mensagem)
    else:
        messages.error(request, mensagem)
    
    return redirect('processos:detalhes', processo_id=processo_id)


@login_required
def editar_dados(request, processo_id):
    """Edita os dados do formulário do processo"""
    processo = get_object_or_404(InstanciaProcesso, id=processo_id)
    
    # Verifica permissão
    if not processo._usuario_tem_permissao_fase(request.user, processo.fase_atual):
        if not request.user.is_superuser:
            messages.error(request, 'Você não tem permissão para editar este processo.')
            return redirect('processos:detalhes', processo_id=processo_id)
    
    if request.method == 'POST':
        # Coleta os novos dados do formulário
        novos_dados = {}
        for campo in processo.tipo_processo.campos.all():
            valor = request.POST.get(campo.nome_campo)
            if valor is not None:
                novos_dados[campo.nome_campo] = valor
        
        observacoes = request.POST.get('observacoes', '')
        
        sucesso, mensagem = WorkflowService.editar_dados(
            instancia=processo,
            novos_dados=novos_dados,
            usuario=request.user,
            observacoes=observacoes
        )
        
        if sucesso:
            messages.success(request, mensagem)
            return redirect('processos:detalhes', processo_id=processo_id)
        else:
            messages.error(request, mensagem)
    
    # GET - exibe formulário de edição
    campos = processo.tipo_processo.campos.all().order_by('grupo', 'ordem')
    
    context = {
        'processo': processo,
        'campos': campos,
    }
    
    return render(request, 'processos/editar_dados.html', context)
