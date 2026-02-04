from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """
    Extensão do modelo User do Django
    Adiciona informações específicas do sistema de workflow
    """
    SETOR_CHOICES = [
        ('COMERCIAL', 'Comercial'),
        ('FINANCEIRO', 'Financeiro'),
        ('OPERACOES', 'Operações'),
        ('PD', 'P&D'),
        ('ADMIN', 'Administrativo'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfilusuario',
        verbose_name="Usuário"
    )
    setor = models.CharField(
        max_length=20,
        choices=SETOR_CHOICES,
        verbose_name="Setor",
        help_text="Setor ao qual o usuário pertence"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Usuários inativos não podem acessar o sistema"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_setor_display()}"

    def get_nome_completo(self):
        """Retorna o nome completo do usuário ou username"""
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        # Não cria perfil automaticamente, será criado manualmente no admin
        pass


@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    if hasattr(instance, 'perfilusuario'):
        instance.perfilusuario.save()
