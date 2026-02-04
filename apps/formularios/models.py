from django.db import models
from django.urls import reverse
import uuid
from apps.core.models import TipoProcesso


class FormularioExterno(models.Model):
    """
    Configuração de formulário externo para recebimento de solicitações
    Cada tipo de processo pode ter um formulário externo acessível via token
    """
    tipo_processo = models.OneToOneField(
        TipoProcesso,
        on_delete=models.CASCADE,
        related_name='formulario_externo',
        verbose_name="Tipo de Processo"
    )
    token = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Token",
        help_text="Token único para acesso ao formulário"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Formulários inativos não aceitam novas submissões"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título exibido no formulário externo"
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        help_text="Texto de introdução exibido no formulário"
    )
    mensagem_sucesso = models.TextField(
        default="Sua solicitação foi enviada com sucesso! Em breve entraremos em contato.",
        verbose_name="Mensagem de Sucesso",
        help_text="Mensagem exibida após envio bem-sucedido"
    )
    cor_tema = models.CharField(
        max_length=7,
        default='#0066cc',
        verbose_name="Cor do Tema",
        help_text="Cor principal do formulário (hexadecimal)"
    )
    logo_url = models.URLField(
        blank=True,
        verbose_name="URL da Logo",
        help_text="URL da logo a ser exibida no formulário"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Formulário Externo"
        verbose_name_plural = "Formulários Externos"
        ordering = ['tipo_processo__nome']

    def __str__(self):
        return f"Formulário: {self.tipo_processo.nome}"

    def gerar_link(self, request=None):
        """Gera o link público do formulário"""
        if request:
            return request.build_absolute_uri(
                reverse('formularios:externo', kwargs={'token': self.token})
            )
        return reverse('formularios:externo', kwargs={'token': self.token})

    def processar_submissao(self, dados_formulario, ip_origem=None):
        """
        Processa a submissão do formulário externo
        Cria uma InstanciaProcesso e registra no histórico
        """
        from apps.processos.models import InstanciaProcesso
        from apps.auditoria.models import HistoricoProcesso
        from apps.core.models import Fase
        
        # Obtém a fase inicial do processo
        fase_inicial = Fase.objects.filter(
            tipo_processo=self.tipo_processo,
            fase_inicial=True
        ).first()
        
        if not fase_inicial:
            raise ValueError(
                f"Nenhuma fase inicial configurada para o processo {self.tipo_processo.nome}"
            )
        
        # Cria a instância do processo
        instancia = InstanciaProcesso.objects.create(
            tipo_processo=self.tipo_processo,
            fase_atual=fase_inicial,
            dados=dados_formulario,
            origem='formulario_externo',
            criado_por=None  # Criado externamente
        )
        
        # Registra no histórico
        observacoes = f"Processo criado via formulário externo"
        if ip_origem:
            observacoes += f" (IP: {ip_origem})"
        
        HistoricoProcesso.registrar_criacao(
            instancia_processo=instancia,
            usuario=None,
            observacoes=observacoes
        )
        
        return instancia

    def get_campos_visiveis(self):
        """Retorna apenas os campos visíveis no formulário externo"""
        return self.tipo_processo.campos.filter(
            visivel_formulario_externo=True
        ).order_by('grupo', 'ordem')
