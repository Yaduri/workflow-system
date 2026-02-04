"""
Script para popular o banco de dados com dados de exemplo
Execute: python manage.py shell < populate_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import TipoProcesso, Fase, CampoFormulario
from apps.usuarios.models import PerfilUsuario
from apps.formularios.models import FormularioExterno

print("🚀 Iniciando população do banco de dados...")

# Criar superusuário
print("\n📝 Criando superusuário...")
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@workflow.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema'
    )
    PerfilUsuario.objects.create(
        user=admin,
        setor='ADMIN',
        telefone='(11) 99999-9999',
        ativo=True
    )
    print("✅ Superusuário criado: admin / admin123")
else:
    print("ℹ️  Superusuário já existe")

# Criar usuários de teste
print("\n👥 Criando usuários de teste...")
usuarios_teste = [
    {'username': 'comercial', 'setor': 'COMERCIAL', 'nome': 'João', 'sobrenome': 'Silva'},
    {'username': 'financeiro', 'setor': 'FINANCEIRO', 'nome': 'Maria', 'sobrenome': 'Santos'},
    {'username': 'operacoes', 'setor': 'OPERACOES', 'nome': 'Pedro', 'sobrenome': 'Costa'},
]

for dados in usuarios_teste:
    if not User.objects.filter(username=dados['username']).exists():
        user = User.objects.create_user(
            username=dados['username'],
            password='123456',
            first_name=dados['nome'],
            last_name=dados['sobrenome'],
            email=f"{dados['username']}@workflow.com"
        )
        PerfilUsuario.objects.create(
            user=user,
            setor=dados['setor'],
            telefone='(11) 98888-8888',
            ativo=True
        )
        print(f"✅ Usuário criado: {dados['username']} / 123456")

# Criar Tipo de Processo: Credenciamento TEF/PIX
print("\n📋 Criando tipo de processo: Credenciamento TEF/PIX...")
tipo_processo, created = TipoProcesso.objects.get_or_create(
    nome='Credenciamento TEF/PIX',
    defaults={
        'descricao': 'Processo de credenciamento de estabelecimentos para TEF e PIX',
        'prefixo_numero': 'TEF',
        'ativo': True
    }
)

if created:
    print("✅ Tipo de processo criado")
    
    # Criar Fases
    print("\n🔄 Criando fases do workflow...")
    fases_dados = [
        {'nome': 'Novas Solicitações', 'ordem': 1, 'setor': 'COMERCIAL', 'inicial': True, 'cor': '#6B7280'},
        {'nome': 'Cadastro Interno', 'ordem': 2, 'setor': 'COMERCIAL', 'cor': '#3B82F6'},
        {'nome': 'Análise Financeira', 'ordem': 3, 'setor': 'FINANCEIRO', 'cor': '#F59E0B'},
        {'nome': 'Cadastro TEFHouse', 'ordem': 4, 'setor': 'OPERACOES', 'cor': '#8B5CF6'},
        {'nome': 'Teste de Bancada', 'ordem': 5, 'setor': 'PD', 'cor': '#EC4899'},
        {'nome': 'Aguardando Cliente', 'ordem': 6, 'setor': 'COMERCIAL', 'cor': '#F97316'},
        {'nome': 'Concluído', 'ordem': 7, 'setor': 'TODOS', 'final': True, 'cor': '#10B981'},
    ]
    
    for fase_data in fases_dados:
        Fase.objects.create(
            tipo_processo=tipo_processo,
            nome=fase_data['nome'],
            ordem=fase_data['ordem'],
            setor_responsavel=fase_data['setor'],
            fase_inicial=fase_data.get('inicial', False),
            fase_final=fase_data.get('final', False),
            cor_badge=fase_data['cor'],
            permite_avancar=True,
            permite_retornar=True
        )
        print(f"  ✅ Fase criada: {fase_data['nome']}")
    
    # Criar Campos do Formulário
    print("\n📝 Criando campos do formulário...")
    campos_dados = [
        # Dados da Empresa
        {'nome': 'nome_empresa', 'label': 'Nome da Empresa', 'tipo': 'text', 'grupo': 'Dados da Empresa', 'ordem': 1, 'obrigatorio': True},
        {'nome': 'cnpj', 'label': 'CNPJ', 'tipo': 'text', 'grupo': 'Dados da Empresa', 'ordem': 2, 'obrigatorio': True, 'placeholder': '00.000.000/0000-00'},
        {'nome': 'contato_nome', 'label': 'Nome do Contato', 'tipo': 'text', 'grupo': 'Dados da Empresa', 'ordem': 3, 'obrigatorio': True},
        {'nome': 'contato_email', 'label': 'E-mail do Contato', 'tipo': 'email', 'grupo': 'Dados da Empresa', 'ordem': 4, 'obrigatorio': True},
        {'nome': 'contato_telefone', 'label': 'Telefone do Contato', 'tipo': 'tel', 'grupo': 'Dados da Empresa', 'ordem': 5, 'obrigatorio': True},
        
        # Dados TEF
        {'nome': 'adquirente', 'label': 'Adquirente', 'tipo': 'select', 'grupo': 'Dados TEF', 'ordem': 6, 'obrigatorio': True, 
         'opcoes': ['Cielo', 'Rede', 'Stone', 'PagSeguro', 'Outro']},
        {'nome': 'ec', 'label': 'Número do EC', 'tipo': 'text', 'grupo': 'Dados TEF', 'ordem': 7, 'obrigatorio': True},
        {'nome': 'sak', 'label': 'SAK', 'tipo': 'text', 'grupo': 'Dados TEF', 'ordem': 8, 'obrigatorio': False},
        
        # Dados PIX
        {'nome': 'banco', 'label': 'Banco', 'tipo': 'text', 'grupo': 'Dados PIX', 'ordem': 9, 'obrigatorio': True},
        {'nome': 'chave_pix', 'label': 'Chave PIX', 'tipo': 'text', 'grupo': 'Dados PIX', 'ordem': 10, 'obrigatorio': True},
        {'nome': 'client_id', 'label': 'Client ID', 'tipo': 'text', 'grupo': 'Dados PIX', 'ordem': 11, 'obrigatorio': False},
        {'nome': 'client_secret', 'label': 'Client Secret', 'tipo': 'text', 'grupo': 'Dados PIX', 'ordem': 12, 'obrigatorio': False},
        
        # Observações
        {'nome': 'observacoes', 'label': 'Observações', 'tipo': 'textarea', 'grupo': 'Outros', 'ordem': 13, 'obrigatorio': False},
    ]
    
    for campo_data in campos_dados:
        CampoFormulario.objects.create(
            tipo_processo=tipo_processo,
            nome_campo=campo_data['nome'],
            label=campo_data['label'],
            tipo_campo=campo_data['tipo'],
            grupo=campo_data['grupo'],
            ordem=campo_data['ordem'],
            obrigatorio=campo_data['obrigatorio'],
            placeholder=campo_data.get('placeholder', ''),
            opcoes=campo_data.get('opcoes'),
            visivel_formulario_externo=True
        )
        print(f"  ✅ Campo criado: {campo_data['label']}")
    
    # Criar Formulário Externo
    print("\n🌐 Criando formulário externo...")
    formulario = FormularioExterno.objects.create(
        tipo_processo=tipo_processo,
        ativo=True,
        titulo='Solicitação de Credenciamento TEF/PIX',
        descricao='Preencha o formulário abaixo para solicitar o credenciamento de seu estabelecimento para TEF e PIX.',
        mensagem_sucesso='Sua solicitação foi recebida com sucesso! Nossa equipe entrará em contato em breve.',
        cor_tema='#2D5BFF'
    )
    print(f"✅ Formulário externo criado")
    print(f"🔗 Link do formulário: /formulario/{formulario.token}/")

print("\n✨ População do banco concluída com sucesso!")
print("\n📌 Credenciais de acesso:")
print("   Admin: admin / admin123")
print("   Comercial: comercial / 123456")
print("   Financeiro: financeiro / 123456")
print("   Operações: operacoes / 123456")
