from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['setor', 'telefone', 'ativo']


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_setor', 'is_staff']
    
    def get_setor(self, obj):
        try:
            return obj.perfilusuario.get_setor_display()
        except:
            return '-'
    get_setor.short_description = 'Setor'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'setor', 'telefone', 'ativo']
    list_filter = ['setor', 'ativo']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
