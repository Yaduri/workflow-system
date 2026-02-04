# Sistema de Workflow por Estados

Sistema completo de gestão de processos corporativos baseado em workflow configurável por estados, com formulários dinâmicos e entrada externa de solicitações.

## 🚀 Características Principais

- **Workflow Configurável**: Defina fases, campos e permissões por dados
- **Formulários Dinâmicos**: Campos configuráveis armazenados em JSON
- **Formulários Externos**: Receba solicitações de clientes sem necessidade de login
- **Auditoria Completa**: Histórico imutável de todas as ações
- **Controle de Permissões**: Por setor e usuário
- **Design Único**: Interface moderna e profissional

## 📋 Tecnologias Utilizadas

- **Backend**: Python 3.x + Django 4.2
- **Banco de Dados**: PostgreSQL (Supabase) / SQLite (desenvolvimento)
- **Frontend**: Bootstrap 5 + CSS customizado
- **Autenticação**: Django Auth

## 🛠️ Instalação e Configuração

### 1. Clone o repositório e entre na pasta

```bash
cd c:\Fontes\Python\Formularios
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
copy .env.example .env
```

**Para desenvolvimento (SQLite)**:
- Mantenha as configurações padrão

**Para produção (Supabase)**:
- Configure a variável `DATABASE_URL` com suas credenciais do Supabase:
```
DATABASE_URL=postgresql://usuario:senha@host:porta/database
```

### 5. Execute as migrations

```bash
python manage.py migrate
```

### 6. Popule o banco com dados de exemplo

```bash
python populate_db.py
```

Isso criará:
- Superusuário: `admin` / `admin123`
- Usuários de teste: `comercial`, `financeiro`, `operacoes` (senha: `123456`)
- Tipo de processo: "Credenciamento TEF/PIX"
- Fases do workflow
- Campos do formulário
- Formulário externo

### 7. Inicie o servidor

```bash
python manage.py runserver
```

Acesse: http://localhost:8000

## 📱 Funcionalidades

### 1. Administração (Django Admin)

Acesse `/admin/` com o usuário `admin` / `admin123`

**Configurações disponíveis**:
- **Tipos de Processo**: Crie novos tipos de processos
- **Fases**: Configure o workflow (ordem, setor responsável, permissões)
- **Campos do Formulário**: Defina campos dinâmicos
- **Formulários Externos**: Gere links públicos para receber solicitações
- **Usuários**: Gerencie usuários e perfis

### 2. Sistema Interno

**Listagem de Processos** (`/processos/`):
- Visualize todos os processos
- Filtros por tipo, fase, setor, responsável
- Busca por número ou dados
- Estatísticas em tempo real

**Detalhes do Processo** (`/processos/<id>/`):
- Visualização completa dos dados
- Histórico de todas as ações
- Mudança de fase
- Atribuição de responsável
- Adicionar comentários
- Editar dados do formulário

### 3. Formulário Externo

**Acesso público** (`/formulario/<token>/`):
- Não requer autenticação
- Design customizável (cores, logo)
- Validação de campos
- Criação automática de processo
- Mensagem de sucesso personalizada

**Como obter o link**:
1. Acesse o Django Admin
2. Vá em "Formulários Externos"
3. Copie o link público do formulário

## 🔄 Fluxo de Trabalho

### Exemplo: Credenciamento TEF/PIX

1. **Cliente** acessa o formulário externo e preenche os dados
2. Sistema cria automaticamente um processo na fase "Novas Solicitações"
3. **Comercial** revisa e move para "Cadastro Interno"
4. **Financeiro** analisa e move para "Análise Financeira"
5. **Operações** realiza o "Cadastro TEFHouse"
6. **P&D** executa "Teste de Bancada"
7. Se necessário, retorna para "Aguardando Cliente"
8. Finaliza em "Concluído"

Cada transição é registrada no histórico com:
- Usuário responsável
- Data/hora
- Fase anterior e nova
- Observações

## 🎨 Customização

### Adicionar Novo Tipo de Processo

1. Acesse Django Admin > Tipos de Processos
2. Clique em "Adicionar Tipo de Processo"
3. Preencha:
   - Nome do processo
   - Prefixo para numeração (ex: SUP, FIN)
   - Descrição
4. Na mesma tela, adicione:
   - **Fases**: Defina o workflow
   - **Campos**: Configure os campos do formulário
5. Salve

### Criar Formulário Externo

1. Acesse Django Admin > Formulários Externos
2. Clique em "Adicionar Formulário Externo"
3. Selecione o tipo de processo
4. Configure:
   - Título e descrição
   - Mensagem de sucesso
   - Cor do tema
   - Logo (opcional)
5. Copie o link gerado

## 🔒 Permissões

### Por Setor

Cada fase possui um setor responsável:
- `COMERCIAL`
- `FINANCEIRO`
- `OPERACOES`
- `PD` (P&D)
- `ADMIN`
- `TODOS`

Usuários só podem mover processos para fases do seu setor (ou se forem superusuários).

### Por Usuário

Opcionalmente, você pode restringir fases a usuários específicos:
1. Edite a fase no Django Admin
2. Adicione usuários em "Usuários Autorizados"

## 📊 Estrutura do Banco de Dados

### Modelos Principais

- **TipoProcesso**: Define tipos de processos
- **Fase**: Fases do workflow
- **CampoFormulario**: Campos dinâmicos
- **InstanciaProcesso**: Processos em execução
- **HistoricoProcesso**: Auditoria imutável
- **FormularioExterno**: Configuração de formulários públicos
- **PerfilUsuario**: Extensão do User com setor

## 🐛 Troubleshooting

### Erro ao conectar no Supabase

Verifique a string de conexão no `.env`:
```
DATABASE_URL=postgresql://usuario:senha@host:porta/database
```

### Formulário externo não aparece

Verifique se:
1. O formulário está marcado como "Ativo"
2. O tipo de processo tem campos com "Visível no Formulário Externo" = True
3. Existe pelo menos uma fase com "Fase Inicial" = True

### Usuário não consegue mudar fase

Verifique:
1. O usuário pertence ao setor responsável pela fase de destino
2. A fase atual permite avanço/retorno
3. Todos os campos obrigatórios estão preenchidos

## 📝 Próximos Passos

- [ ] Implementar relatórios e dashboards
- [ ] Adicionar notificações por e-mail
- [ ] Implementar SLA (tempo máximo por fase)
- [ ] Exportação de dados (CSV, Excel)
- [ ] API REST para integrações
- [ ] Anexos de arquivos nos processos

## 👥 Suporte

Para dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.

---

**Desenvolvido com ⚡ por Antigravity AI**
