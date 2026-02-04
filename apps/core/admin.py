from django.contrib import admin
from .models import TipoProcesso, Fase, CampoFormulario


class FaseInline(admin.TabularInline):
    model = Fase
    extra = 1
    fields = ['nome', 'ordem', 'setor_responsavel', 'fase_inicial', 'fase_final', 'cor_badge']
    ordering = ['ordem']


class CampoFormularioInline(admin.TabularInline):
    model = CampoFormulario
    extra = 1
    fields = ['nome_campo', 'label', 'tipo_campo', 'obrigatorio', 'ordem', 'grupo', 'visivel_formulario_externo']
    ordering = ['grupo', 'ordem']


@admin.register(TipoProcesso)
class TipoProcessoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'prefixo_numero', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
    inlines = [FaseInline, CampoFormularioInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'prefixo_numero', 'descricao', 'ativo')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Fase)
class FaseAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo_processo', 'ordem', 'setor_responsavel', 'fase_inicial', 'fase_final']
    list_filter = ['tipo_processo', 'setor_responsavel', 'fase_inicial', 'fase_final']
    search_fields = ['nome', 'tipo_processo__nome']
    filter_horizontal = ['usuarios_autorizados']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo_processo', 'nome', 'ordem', 'setor_responsavel')
        }),
        ('Configurações de Workflow', {
            'fields': ('fase_inicial', 'fase_final', 'permite_avancar', 'permite_retornar')
        }),
        ('Permissões', {
            'fields': ('usuarios_autorizados',),
            'description': 'Deixe vazio para permitir todos os usuários do setor'
        }),
        ('Aparência', {
            'fields': ('cor_badge',)
        }),
    )


@admin.register(CampoFormulario)
class CampoFormularioAdmin(admin.ModelAdmin):
    list_display = ['label', 'tipo_processo', 'nome_campo', 'tipo_campo', 'obrigatorio', 'grupo', 'ordem', 'visivel_formulario_externo']
    list_filter = ['tipo_processo', 'tipo_campo', 'obrigatorio', 'visivel_formulario_externo', 'grupo']
    search_fields = ['label', 'nome_campo', 'tipo_processo__nome']
    filter_horizontal = ['obrigatorio_em_fases']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo_processo', 'nome_campo', 'label', 'tipo_campo')
        }),
        ('Configurações do Campo', {
            'fields': ('placeholder', 'ajuda', 'opcoes', 'validacao_regex')
        }),
        ('Obrigatoriedade', {
            'fields': ('obrigatorio', 'obrigatorio_em_fases')
        }),
        ('Organização', {
            'fields': ('grupo', 'ordem', 'visivel_formulario_externo')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Adiciona help text para o campo opcoes
        if 'opcoes' in form.base_fields:
            form.base_fields['opcoes'].help_text = (
                'Para campos select/radio/checkbox, use formato JSON. '
                'Exemplos: ["Opção 1", "Opção 2"] ou '
                '[{"value": "sim", "label": "Sim"}, {"value": "nao", "label": "Não"}]'
            )
        return form
