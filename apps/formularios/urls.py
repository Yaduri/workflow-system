from django.urls import path
from . import views

app_name = 'formularios'

urlpatterns = [
    path('<str:token>/', views.formulario_externo, name='externo'),
]
