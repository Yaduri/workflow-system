from django.contrib import admin
from .models import FormularioExterno


@admin.register(FormularioExterno)
class FormularioExternoAdmin(admin.ModelAdmin):
    list_display = ['tipo_processo', 'ativo', 'get_link', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['tipo_processo__nome', 'titulo']
    readonly_fields = ['token', 'criado_em', 'atualizado_em', 'get_link_completo']
    
    fieldsets = (
        ('Configuração', {
            'fields': ('tipo_processo', 'ativo', 'token')
        }),
        ('Conteúdo', {
            'fields': ('titulo', 'descricao', 'mensagem_sucesso')
        }),
        ('Aparência', {
            'fields': ('cor_tema', 'logo_url')
        }),
        ('Link de Acesso', {
            'fields': ('get_link_completo',),
            'description': 'Compartilhe este link para permitir submissões externas'
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def get_link(self, obj):
        return f"/formulario/{obj.token}"
    get_link.short_description = 'Link'
    
    def get_link_completo(self, obj):
        from django.utils.html import format_html
        link = f"/formulario/{obj.token}"
        return format_html(
            '<a href="{}" target="_blank">{}</a><br><br>'
            '<input type="text" value="{}" readonly style="width: 100%; padding: 8px;" '
            'onclick="this.select(); document.execCommand(\'copy\'); alert(\'Link copiado!\');">',
            link, link, link
        )
    get_link_completo.short_description = 'Link Público'
