from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TipoProcesso, Fase


class InstanciaProcesso(models.Model):
    """
    Representa uma instância de processo em execução
    Armazena os dados do formulário em JSONField para flexibilidade
    """
    ORIGEM_CHOICES = [
        ('formulario_externo', 'Formulário Externo'),
        ('criacao_interna', 'Criação Interna'),
    ]

    tipo_processo = models.ForeignKey(
        TipoProcesso,
        on_delete=models.PROTECT,
        related_name='instancias',
        verbose_name="Tipo de Processo"
    )
    numero = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Processo",
        help_text="Gerado automaticamente (ex: TEF-2026-001)"
    )
    fase_atual = models.ForeignKey(
        Fase,
        on_delete=models.PROTECT,
        related_name='processos_nesta_fase',
        verbose_name="Fase Atual"
    )
    dados = models.JSONField(
        default=dict,
        verbose_name="Dados do Formulário",
        help_text="Dados dinâmicos do formulário armazenados em JSON"
    )
    responsavel_atual = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_responsavel',
        verbose_name="Responsável Atual"
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_criados',
        verbose_name="Criado Por",
        help_text="Usuário que criou o processo (null se criado via formulário externo)"
    )
    origem = models.CharField(
        max_length=20,
        choices=ORIGEM_CHOICES,
        default='criacao_interna',
        verbose_name="Origem"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['tipo_processo', 'fase_atual']),
            models.Index(fields=['responsavel_atual']),
            models.Index(fields=['-criado_em']),
        ]

    def __str__(self):
        return f"{self.numero} - {self.tipo_processo.nome}"

    def save(self, *args, **kwargs):
        """Gera número automático se não existir"""
        if not self.numero:
            self.numero = self.gerar_numero()
        super().save(*args, **kwargs)

    def gerar_numero(self):
        """
        Gera número sequencial do processo
        Formato: PREFIXO-ANO-SEQUENCIA (ex: TEF-2026-001)
        """
        ano_atual = timezone.now().year
        sequencia = self.tipo_processo.get_proxima_sequencia()
        return f"{self.tipo_processo.prefixo_numero}-{ano_atual}-{sequencia:03d}"

    def pode_avancar_fase(self, usuario):
        """Verifica se o usuário pode avançar a fase do processo"""
        if not self.fase_atual.permite_avancar:
            return False
        
        # Verifica se o usuário tem permissão para a fase atual
        return self._usuario_tem_permissao_fase(usuario, self.fase_atual)

    def pode_retornar_fase(self, usuario):
        """Verifica se o usuário pode retornar a fase do processo"""
        if not self.fase_atual.permite_retornar:
            return False
        
        return self._usuario_tem_permissao_fase(usuario, self.fase_atual)

    def _usuario_tem_permissao_fase(self, usuario, fase):
        """Verifica se o usuário tem permissão para atuar na fase"""
        # Superusuário tem acesso total
        if usuario.is_superuser:
            return True
        
        # Verifica se há usuários específicos autorizados
        usuarios_autorizados = fase.usuarios_autorizados.all()
        if usuarios_autorizados.exists():
            return usuario in usuarios_autorizados
        
        # Verifica se o usuário pertence ao setor responsável
        try:
            perfil = usuario.perfilusuario
            if fase.setor_responsavel == 'TODOS':
                return True
            return perfil.setor == fase.setor_responsavel
        except:
            return False

    def validar_campos_obrigatorios(self, fase):
        """
        Valida se todos os campos obrigatórios para a fase estão preenchidos
        Retorna (valido, campos_faltantes)
        """
        from apps.core.models import CampoFormulario
        
        campos_faltantes = []
        
        # Campos obrigatórios globalmente
        campos_obrigatorios = CampoFormulario.objects.filter(
            tipo_processo=self.tipo_processo,
            obrigatorio=True
        )
        
        for campo in campos_obrigatorios:
            valor = self.dados.get(campo.nome_campo)
            if not valor or (isinstance(valor, str) and not valor.strip()):
                campos_faltantes.append(campo.label)
        
        # Campos obrigatórios na fase específica
        campos_fase = fase.campos_obrigatorios.all()
        for campo in campos_fase:
            valor = self.dados.get(campo.nome_campo)
            if not valor or (isinstance(valor, str) and not valor.strip()):
                if campo.label not in campos_faltantes:
                    campos_faltantes.append(campo.label)
        
        return (len(campos_faltantes) == 0, campos_faltantes)

    def get_fases_disponiveis(self, usuario):
        """
        Retorna as fases para as quais o processo pode ser movido
        considerando as permissões do usuário
        """
        fases_disponiveis = []
        todas_fases = Fase.objects.filter(tipo_processo=self.tipo_processo).order_by('ordem')
        
        for fase in todas_fases:
            if fase.id == self.fase_atual.id:
                continue
            
            # Verifica se pode avançar ou retornar
            if fase.ordem > self.fase_atual.ordem and not self.fase_atual.permite_avancar:
                continue
            if fase.ordem < self.fase_atual.ordem and not self.fase_atual.permite_retornar:
                continue
            
            # Verifica permissão do usuário
            if self._usuario_tem_permissao_fase(usuario, fase):
                fases_disponiveis.append(fase)
        
        return fases_disponiveis

    def get_dados_formatados(self):
        """Retorna os dados do processo formatados e agrupados"""
        from apps.core.models import CampoFormulario
        
        dados_formatados = {}
        campos = CampoFormulario.objects.filter(
            tipo_processo=self.tipo_processo
        ).order_by('ordem', 'id')
        
        for campo in campos:
            grupo_nome = campo.grupo or 'Informações Gerais'
            valor = self.dados.get(campo.nome_campo, '')
            
            if grupo_nome not in dados_formatados:
                dados_formatados[grupo_nome] = {}
            
            dados_formatados[grupo_nome][campo.label] = {
                'valor': valor,
                'tipo': campo.tipo_campo,
            }
        
        return dados_formatados
