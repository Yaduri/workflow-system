"""
URL configuration for config project.
Sistema de Workflow por Estados
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Apps
    path('processos/', include('apps.processos.urls')),
    path('formulario/', include('apps.formularios.urls')),
    path('configuracoes/', include('apps.core.urls')),
    
    # Redirect raiz para lista de processos
    path('', RedirectView.as_view(url='/processos/', permanent=False)),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customização do Admin
admin.site.site_header = "Sistema de Workflow"
admin.site.site_title = "Workflow Admin"
admin.site.index_title = "Administração do Sistema"
