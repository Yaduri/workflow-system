"""
Serviço de Workflow
Gerencia as transições de fase e validações do processo
"""
from django.db import transaction
from apps.auditoria.models import HistoricoProcesso


class WorkflowService:
    """
    Serviço centralizado para gerenciar o workflow dos processos
    """

    @staticmethod
    @transaction.atomic
    def transicionar_fase(instancia, nova_fase, usuario, observacoes=''):
        """
        Realiza a transição de fase de um processo
        
        Args:
            instancia: InstanciaProcesso
            nova_fase: Fase de destino
            usuario: User que está realizando a transição
            observacoes: Observações sobre a transição
        
        Returns:
            (sucesso: bool, mensagem: str)
        """
        # Validações
        valido, mensagem = WorkflowService.validar_transicao(instancia, nova_fase, usuario)
        if not valido:
            return False, mensagem
        
        # Valida campos obrigatórios
        campos_validos, campos_faltantes = instancia.validar_campos_obrigatorios(nova_fase)
        if not campos_validos:
            campos_str = ', '.join(campos_faltantes)
            return False, f"Campos obrigatórios não preenchidos: {campos_str}"
        
        # Salva fase anterior
        fase_anterior = instancia.fase_atual
        
        # Atualiza a fase
        instancia.fase_atual = nova_fase
        instancia.save()
        
        # Registra no histórico
        HistoricoProcesso.registrar_mudanca_fase(
            instancia_processo=instancia,
            fase_anterior=fase_anterior,
            fase_nova=nova_fase,
            usuario=usuario,
            observacoes=observacoes
        )
        
        return True, f"Processo movido para a fase: {nova_fase.nome}"

    @staticmethod
    def validar_transicao(instancia, nova_fase, usuario):
        """
        Valida se a transição de fase é permitida
        
        Returns:
            (valido: bool, mensagem: str)
        """
        # Verifica se a nova fase pertence ao mesmo tipo de processo
        if nova_fase.tipo_processo != instancia.tipo_processo:
            return False, "A fase selecionada não pertence a este tipo de processo"
        
        # Verifica se não é a mesma fase
        if nova_fase.id == instancia.fase_atual.id:
            return False, "O processo já está nesta fase"
        
        # Verifica se é avanço ou retorno
        eh_avanco = nova_fase.ordem > instancia.fase_atual.ordem
        eh_retorno = nova_fase.ordem < instancia.fase_atual.ordem
        
        # Valida permissões de avanço/retorno
        if eh_avanco and not instancia.fase_atual.permite_avancar:
            return False, "A fase atual não permite avanço"
        
        if eh_retorno and not instancia.fase_atual.permite_retornar:
            return False, "A fase atual não permite retorno"
        
        # Valida permissão do usuário
        if not instancia._usuario_tem_permissao_fase(usuario, nova_fase):
            return False, "Você não tem permissão para mover o processo para esta fase"
        
        return True, "Transição válida"

    @staticmethod
    def obter_fases_disponiveis(instancia, usuario):
        """
        Retorna as fases disponíveis para transição
        
        Returns:
            list[Fase]
        """
        return instancia.get_fases_disponiveis(usuario)

    @staticmethod
    @transaction.atomic
    def atribuir_responsavel(instancia, novo_responsavel, usuario_que_atribuiu, observacoes=''):
        """
        Atribui um responsável ao processo
        
        Returns:
            (sucesso: bool, mensagem: str)
        """
        responsavel_anterior = instancia.responsavel_atual
        
        instancia.responsavel_atual = novo_responsavel
        instancia.save()
        
        HistoricoProcesso.registrar_atribuicao(
            instancia_processo=instancia,
            usuario_responsavel_anterior=responsavel_anterior,
            usuario_responsavel_novo=novo_responsavel,
            usuario_que_atribuiu=usuario_que_atribuiu,
            observacoes=observacoes
        )
        
        return True, f"Processo atribuído para {novo_responsavel.get_full_name() or novo_responsavel.username}"

    @staticmethod
    @transaction.atomic
    def editar_dados(instancia, novos_dados, usuario, observacoes=''):
        """
        Edita os dados do formulário do processo
        
        Args:
            instancia: InstanciaProcesso
            novos_dados: dict com os novos dados
            usuario: User que está editando
            observacoes: Observações sobre a edição
        
        Returns:
            (sucesso: bool, mensagem: str)
        """
        # Identifica campos alterados
        campos_alterados = {}
        for campo, valor in novos_dados.items():
            valor_anterior = instancia.dados.get(campo)
            if valor_anterior != valor:
                campos_alterados[campo] = {
                    'anterior': valor_anterior,
                    'novo': valor
                }
        
        if not campos_alterados:
            return False, "Nenhuma alteração detectada"
        
        # Atualiza os dados
        instancia.dados.update(novos_dados)
        instancia.save()
        
        # Registra no histórico
        HistoricoProcesso.registrar_edicao_dados(
            instancia_processo=instancia,
            usuario=usuario,
            campos_alterados=campos_alterados,
            observacoes=observacoes
        )
        
        return True, "Dados atualizados com sucesso"

    @staticmethod
    @transaction.atomic
    def adicionar_comentario(instancia, usuario, comentario):
        """
        Adiciona um comentário ao processo
        
        Returns:
            (sucesso: bool, mensagem: str)
        """
        if not comentario or not comentario.strip():
            return False, "O comentário não pode estar vazio"
        
        HistoricoProcesso.registrar_comentario(
            instancia_processo=instancia,
            usuario=usuario,
            comentario=comentario
        )
        
        return True, "Comentário adicionado com sucesso"
