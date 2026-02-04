from django.contrib import admin
from .models import HistoricoProcesso


@admin.register(HistoricoProcesso)
class HistoricoProcessoAdmin(admin.ModelAdmin):
    list_display = ['instancia_processo', 'tipo_evento', 'fase_anterior', 'fase_nova', 'usuario', 'criado_em']
    list_filter = ['tipo_evento', 'criado_em']
    search_fields = ['instancia_processo__numero', 'observacoes']
    readonly_fields = ['instancia_processo', 'tipo_evento', 'fase_anterior', 'fase_nova', 
                       'usuario', 'observacoes', 'dados_alterados', 'criado_em']
    
    def has_add_permission(self, request):
        """Impede criação manual de histórico"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Impede edição de histórico"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Impede exclusão de histórico"""
        return False
