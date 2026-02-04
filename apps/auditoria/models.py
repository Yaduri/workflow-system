from django.db import models
from django.contrib.auth.models import User
from apps.processos.models import InstanciaProcesso
from apps.core.models import Fase


class HistoricoProcesso(models.Model):
    """
    Registro imutável de eventos do processo
    Mantém auditoria completa de todas as ações
    """
    TIPO_EVENTO_CHOICES = [
        ('criacao', 'Criação do Processo'),
        ('mudanca_fase', 'Mudança de Fase'),
        ('edicao_dados', 'Edição de Dados'),
        ('atribuicao', 'Atribuição de Responsável'),
        ('comentario', 'Comentário'),
    ]

    instancia_processo = models.ForeignKey(
        InstanciaProcesso,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name="Processo"
    )
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name="Tipo de Evento"
    )
    fase_anterior = models.ForeignKey(
        Fase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historico_fase_anterior',
        verbose_name="Fase Anterior"
    )
    fase_nova = models.ForeignKey(
        Fase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historico_fase_nova',
        verbose_name="Fase Nova"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historico_acoes',
        verbose_name="Usuário",
        help_text="Usuário que realizou a ação (null se ação automática)"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Comentários ou observações sobre a ação"
    )
    dados_alterados = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Dados Alterados",
        help_text="Snapshot das alterações realizadas"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora"
    )

    class Meta:
        verbose_name = "Histórico do Processo"
        verbose_name_plural = "Histórico dos Processos"
        ordering = ['-criado_em']
        # Impede edição e exclusão
        permissions = []
        indexes = [
            models.Index(fields=['instancia_processo', '-criado_em']),
            models.Index(fields=['tipo_evento']),
        ]

    def __str__(self):
        return f"{self.instancia_processo.numero} - {self.get_tipo_evento_display()} - {self.criado_em.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        """Permite apenas criação, não edição"""
        if self.pk:
            raise ValueError("Registros de histórico não podem ser editados")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Impede exclusão de registros de histórico"""
        raise ValueError("Registros de histórico não podem ser excluídos")

    @classmethod
    def registrar_criacao(cls, instancia_processo, usuario=None, observacoes=''):
        """Registra a criação de um processo"""
        return cls.objects.create(
            instancia_processo=instancia_processo,
            tipo_evento='criacao',
            fase_nova=instancia_processo.fase_atual,
            usuario=usuario,
            observacoes=observacoes or 'Processo criado',
            dados_alterados={'origem': instancia_processo.origem}
        )

    @classmethod
    def registrar_mudanca_fase(cls, instancia_processo, fase_anterior, fase_nova, usuario, observacoes=''):
        """Registra mudança de fase"""
        return cls.objects.create(
            instancia_processo=instancia_processo,
            tipo_evento='mudanca_fase',
            fase_anterior=fase_anterior,
            fase_nova=fase_nova,
            usuario=usuario,
            observacoes=observacoes,
            dados_alterados={
                'fase_anterior_nome': fase_anterior.nome if fase_anterior else None,
                'fase_nova_nome': fase_nova.nome,
            }
        )

    @classmethod
    def registrar_edicao_dados(cls, instancia_processo, usuario, campos_alterados, observacoes=''):
        """Registra edição de dados do formulário"""
        return cls.objects.create(
            instancia_processo=instancia_processo,
            tipo_evento='edicao_dados',
            usuario=usuario,
            observacoes=observacoes or 'Dados do formulário editados',
            dados_alterados=campos_alterados
        )

    @classmethod
    def registrar_atribuicao(cls, instancia_processo, usuario_responsavel_anterior, usuario_responsavel_novo, usuario_que_atribuiu, observacoes=''):
        """Registra atribuição de responsável"""
        return cls.objects.create(
            instancia_processo=instancia_processo,
            tipo_evento='atribuicao',
            usuario=usuario_que_atribuiu,
            observacoes=observacoes or 'Responsável atribuído',
            dados_alterados={
                'responsavel_anterior': usuario_responsavel_anterior.username if usuario_responsavel_anterior else None,
                'responsavel_novo': usuario_responsavel_novo.username if usuario_responsavel_novo else None,
            }
        )

    @classmethod
    def registrar_comentario(cls, instancia_processo, usuario, comentario):
        """Registra um comentário no processo"""
        return cls.objects.create(
            instancia_processo=instancia_processo,
            tipo_evento='comentario',
            usuario=usuario,
            observacoes=comentario
        )
