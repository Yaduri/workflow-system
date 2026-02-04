from django.contrib import admin
from .models import InstanciaProcesso


@admin.register(InstanciaProcesso)
class InstanciaProcessoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'tipo_processo', 'fase_atual', 'responsavel_atual', 'origem', 'criado_em']
    list_filter = ['tipo_processo', 'fase_atual', 'origem', 'criado_em']
    search_fields = ['numero', 'dados']
    readonly_fields = ['numero', 'criado_em', 'atualizado_em', 'criado_por']
    
    fieldsets = (
        ('Informações do Processo', {
            'fields': ('numero', 'tipo_processo', 'fase_atual', 'origem')
        }),
        ('Responsabilidade', {
            'fields': ('responsavel_atual', 'criado_por')
        }),
        ('Dados do Formulário', {
            'fields': ('dados',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        """Impede exclusão de processos pelo admin"""
        return request.user.is_superuser
