from django.urls import path
from . import views

app_name = 'configuracoes'

urlpatterns = [
    # Dashboard
    path('', views.configuracoes_index, name='index'),
    
    # Tipos de Processo
    path('tipos-processo/', views.tipos_processo_lista, name='tipos_processo_lista'),
    path('tipos-processo/criar/', views.tipos_processo_criar, name='tipos_processo_criar'),
    path('tipos-processo/<int:tipo_id>/editar/', views.tipos_processo_editar, name='tipos_processo_editar'),
    
    # Fases
    path('tipos-processo/<int:tipo_id>/fases/', views.fases_gerenciar, name='fases_gerenciar'),
    
    # Campos
    path('tipos-processo/<int:tipo_id>/campos/', views.campos_gerenciar, name='campos_gerenciar'),
    
    # Formulários Externos
    path('formularios-externos/', views.formularios_externos_lista, name='formularios_externos_lista'),
    path('formularios-externos/criar/', views.formularios_externos_criar, name='formularios_externos_criar'),
    
    # Usuários
    path('usuarios/', views.usuarios_lista, name='usuarios_lista'),
    path('usuarios/criar/', views.usuarios_criar, name='usuarios_criar'),
]
