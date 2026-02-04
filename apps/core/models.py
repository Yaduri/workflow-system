from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class TipoProcesso(models.Model):
    """
    Define um tipo de processo (ex: Credenciamento TEF/PIX, Solicitação de Suporte, etc.)
    Cada tipo de processo possui seu próprio workflow e campos de formulário
    """
    nome = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Nome do Processo",
        help_text="Ex: Credenciamento TEF/PIX"
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição detalhada do processo"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Processos inativos não podem receber novas solicitações"
    )
    prefixo_numero = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Prefixo do Número",
        help_text="Prefixo para numeração automática (ex: TEF, SUP, FIN)",
        validators=[RegexValidator(regex=r'^[A-Z]+$', message='Apenas letras maiúsculas')]
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Tipo de Processo"
        verbose_name_plural = "Tipos de Processos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_proxima_sequencia(self):
        """Retorna o próximo número sequencial para este tipo de processo"""
        from apps.processos.models import InstanciaProcesso
        ultimo = InstanciaProcesso.objects.filter(
            tipo_processo=self
        ).order_by('-id').first()
        
        if ultimo and ultimo.numero:
            # Extrai o número da sequência (ex: TEF-2026-001 -> 1)
            try:
                partes = ultimo.numero.split('-')
                if len(partes) >= 3:
                    return int(partes[-1]) + 1
            except (ValueError, IndexError):
                pass
        return 1


class Fase(models.Model):
    """
    Define uma fase do workflow de um tipo de processo
    Ex: Novas Solicitações, Cadastro Interno, Teste de Bancada, etc.
    """
    SETOR_CHOICES = [
        ('COMERCIAL', 'Comercial'),
        ('FINANCEIRO', 'Financeiro'),
        ('OPERACOES', 'Operações'),
        ('PD', 'P&D'),
        ('ADMIN', 'Administrativo'),
        ('TODOS', 'Todos os Setores'),
    ]

    tipo_processo = models.ForeignKey(
        TipoProcesso,
        on_delete=models.CASCADE,
        related_name='fases',
        verbose_name="Tipo de Processo"
    )
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome da Fase",
        help_text="Ex: Novas Solicitações, Cadastro Interno"
    )
    ordem = models.IntegerField(
        verbose_name="Ordem",
        help_text="Ordem sequencial da fase no workflow (1, 2, 3...)"
    )
    setor_responsavel = models.CharField(
        max_length=20,
        choices=SETOR_CHOICES,
        verbose_name="Setor Responsável",
        help_text="Setor responsável por esta fase"
    )
    usuarios_autorizados = models.ManyToManyField(
        User,
        blank=True,
        related_name='fases_autorizadas',
        verbose_name="Usuários Autorizados",
        help_text="Usuários específicos autorizados (deixe vazio para permitir todo o setor)"
    )
    permite_avancar = models.BooleanField(
        default=True,
        verbose_name="Permite Avançar",
        help_text="Permite avançar para a próxima fase"
    )
    permite_retornar = models.BooleanField(
        default=True,
        verbose_name="Permite Retornar",
        help_text="Permite retornar para fase anterior"
    )
    fase_inicial = models.BooleanField(
        default=False,
        verbose_name="Fase Inicial",
        help_text="Marca como fase inicial do processo (criação via formulário externo)"
    )
    fase_final = models.BooleanField(
        default=False,
        verbose_name="Fase Final",
        help_text="Marca como fase de conclusão do processo"
    )
    cor_badge = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name="Cor do Badge",
        help_text="Cor hexadecimal para exibição (ex: #007bff)"
    )

    class Meta:
        verbose_name = "Fase"
        verbose_name_plural = "Fases"
        ordering = ['tipo_processo', 'ordem']
        unique_together = [['tipo_processo', 'ordem'], ['tipo_processo', 'nome']]

    def __str__(self):
        return f"{self.tipo_processo.nome} - {self.nome}"


class CampoFormulario(models.Model):
    """
    Define um campo dinâmico do formulário de um tipo de processo
    Os dados serão armazenados em JSONField na InstanciaProcesso
    """
    TIPO_CAMPO_CHOICES = [
        ('text', 'Texto Curto'),
        ('textarea', 'Texto Longo'),
        ('number', 'Número'),
        ('email', 'E-mail'),
        ('tel', 'Telefone'),
        ('date', 'Data'),
        ('select', 'Seleção (Dropdown)'),
        ('radio', 'Seleção (Radio)'),
        ('checkbox', 'Múltipla Escolha'),
        ('file', 'Arquivo'),
    ]

    tipo_processo = models.ForeignKey(
        TipoProcesso,
        on_delete=models.CASCADE,
        related_name='campos',
        verbose_name="Tipo de Processo"
    )
    nome_campo = models.CharField(
        max_length=100,
        verbose_name="Nome do Campo",
        help_text="Nome técnico do campo (sem espaços, ex: cnpj_empresa)",
        validators=[RegexValidator(
            regex=r'^[a-z][a-z0-9_]*$',
            message='Use apenas letras minúsculas, números e underscore. Deve começar com letra.'
        )]
    )
    label = models.CharField(
        max_length=200,
        verbose_name="Rótulo",
        help_text="Texto exibido para o usuário (ex: CNPJ da Empresa)"
    )
    tipo_campo = models.CharField(
        max_length=20,
        choices=TIPO_CAMPO_CHOICES,
        verbose_name="Tipo de Campo"
    )
    opcoes = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Opções",
        help_text='Para campos select/radio/checkbox. Ex: ["Opção 1", "Opção 2"] ou [{"value": "1", "label": "Opção 1"}]'
    )
    obrigatorio = models.BooleanField(
        default=False,
        verbose_name="Obrigatório",
        help_text="Campo obrigatório em todas as fases"
    )
    obrigatorio_em_fases = models.ManyToManyField(
        Fase,
        blank=True,
        related_name='campos_obrigatorios',
        verbose_name="Obrigatório nas Fases",
        help_text="Fases onde este campo é obrigatório"
    )
    ordem = models.IntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição do campo"
    )
    grupo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Grupo",
        help_text="Agrupa campos visualmente (ex: Dados da Empresa, Dados TEF)"
    )
    ajuda = models.TextField(
        blank=True,
        verbose_name="Texto de Ajuda",
        help_text="Texto de ajuda exibido abaixo do campo"
    )
    validacao_regex = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Validação (Regex)",
        help_text="Expressão regular para validação customizada"
    )
    placeholder = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Placeholder",
        help_text="Texto de exemplo dentro do campo"
    )
    visivel_formulario_externo = models.BooleanField(
        default=True,
        verbose_name="Visível no Formulário Externo",
        help_text="Se desmarcado, o campo só aparece internamente"
    )

    class Meta:
        verbose_name = "Campo do Formulário"
        verbose_name_plural = "Campos do Formulário"
        ordering = ['tipo_processo', 'grupo', 'ordem']
        unique_together = [['tipo_processo', 'nome_campo']]

    def __str__(self):
        return f"{self.tipo_processo.nome} - {self.label}"
