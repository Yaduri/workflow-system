from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import FormularioExterno
from apps.core.models import CampoFormulario


def formulario_externo(request, token):
    """
    View pública para formulário externo
    Não requer autenticação
    """
    formulario = get_object_or_404(FormularioExterno, token=token, ativo=True)
    
    if request.method == 'POST':
        # Processa a submissão
        dados_formulario = {}
        erros = []
        
        # Obtém os campos visíveis
        campos = formulario.get_campos_visiveis()
        
        # Valida e coleta os dados
        for campo in campos:
            valor = request.POST.get(campo.nome_campo, '').strip()
            
            # Valida campos obrigatórios
            if campo.obrigatorio and not valor:
                erros.append(f'O campo "{campo.label}" é obrigatório.')
                continue
            
            # Valida regex se configurado
            if campo.validacao_regex and valor:
                import re
                if not re.match(campo.validacao_regex, valor):
                    erros.append(f'O campo "{campo.label}" está em formato inválido.')
                    continue
            
            dados_formulario[campo.nome_campo] = valor
        
        if erros:
            context = {
                'formulario': formulario,
                'campos': campos,
                'erros': erros,
                'dados': dados_formulario,
            }
            return render(request, 'formularios/externo.html', context)
        
        # Processa a submissão
        try:
            # Obtém IP do cliente
            ip_origem = request.META.get('REMOTE_ADDR')
            
            # Cria o processo
            instancia = formulario.processar_submissao(
                dados_formulario=dados_formulario,
                ip_origem=ip_origem
            )
            
            # Redireciona para página de sucesso
            return render(request, 'formularios/sucesso.html', {
                'formulario': formulario,
                'numero_processo': instancia.numero,
            })
            
        except Exception as e:
            erros.append(f'Erro ao processar formulário: {str(e)}')
            context = {
                'formulario': formulario,
                'campos': campos,
                'erros': erros,
                'dados': dados_formulario,
            }
            return render(request, 'formularios/externo.html', context)
    
    # GET - exibe o formulário
    campos = formulario.get_campos_visiveis()
    
    # Agrupa campos por grupo
    grupos = {}
    for campo in campos:
        grupo_nome = campo.grupo or 'Informações Gerais'
        if grupo_nome not in grupos:
            grupos[grupo_nome] = []
        grupos[grupo_nome].append(campo)
    
    context = {
        'formulario': formulario,
        'grupos': grupos,
    }
    
    return render(request, 'formularios/externo.html', context)
