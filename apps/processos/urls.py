from django.urls import path
from . import views

app_name = 'processos'

urlpatterns = [
    path('', views.lista_processos, name='lista'),
    path('<int:processo_id>/', views.detalhes_processo, name='detalhes'),
    path('<int:processo_id>/mudar-fase/', views.mudar_fase, name='mudar_fase'),
    path('<int:processo_id>/atribuir/', views.atribuir_responsavel, name='atribuir_responsavel'),
    path('<int:processo_id>/comentario/', views.adicionar_comentario, name='adicionar_comentario'),
    path('<int:processo_id>/editar/', views.editar_dados, name='editar_dados'),
]
