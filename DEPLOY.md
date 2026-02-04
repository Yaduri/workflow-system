# 🚀 Deploy no Render - Guia Completo

## 📋 Pré-requisitos

- Conta no GitHub
- Conta no Render (https://render.com)
- Banco PostgreSQL criado no Render

## 🔧 Passo 1: Preparar o Repositório Git

### 1.1 Inicializar Git (se ainda não fez)

```bash
git init
git add .
git commit -m "Initial commit - Sistema de Workflow"
```

### 1.2 Criar repositório no GitHub

1. Acesse https://github.com/new
2. Crie um novo repositório (ex: `workflow-system`)
3. **NÃO** inicialize com README, .gitignore ou license

### 1.3 Enviar código para o GitHub

```bash
git remote add origin https://github.com/SEU-USUARIO/workflow-system.git
git branch -M main
git push -u origin main
```

## 🌐 Passo 2: Deploy no Render

### 2.1 Criar Web Service

1. Acesse https://dashboard.render.com
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Selecione o repositório `workflow-system`

### 2.2 Configurar o Web Service

Preencha os campos:

- **Name**: `workflow-system` (ou o nome que preferir)
- **Region**: Escolha a mais próxima (ex: Oregon)
- **Branch**: `main`
- **Root Directory**: (deixe em branco)
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn config.wsgi:application`

### 2.3 Configurar Variáveis de Ambiente

Clique em **"Advanced"** e adicione as seguintes variáveis:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Gere uma chave segura (use https://djecrety.ir/) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `workflow-system.onrender.com` (substitua pelo seu domínio) |
| `DATABASE_URL` | Cole a **Internal Database URL** do seu PostgreSQL |
| `PYTHON_VERSION` | `3.11.0` |

**IMPORTANTE**: Use a **Internal Database URL** do PostgreSQL que você criou no Render!

### 2.4 Iniciar Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o build (pode levar 5-10 minutos)
3. O Render vai:
   - Instalar dependências
   - Coletar arquivos estáticos
   - Rodar migrações
   - Popular o banco de dados

## ✅ Passo 3: Verificar Deploy

Após o deploy concluir:

1. Acesse a URL fornecida pelo Render (ex: `https://workflow-system.onrender.com`)
2. Faça login com: `admin` / `admin123`
3. Teste o sistema!

## 🔄 Atualizações Futuras

Para atualizar o site após fazer mudanças:

```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

O Render vai fazer o deploy automaticamente!

## 🔒 Segurança em Produção

Após o primeiro deploy, **ALTERE A SENHA DO ADMIN**:

1. Acesse `/admin/`
2. Vá em **Users** → **admin**
3. Clique em **"change password"**
4. Defina uma senha forte

## 🐛 Troubleshooting

### Build falhou?

Verifique os logs no Render e certifique-se que:
- `build.sh` tem permissão de execução
- Todas as variáveis de ambiente estão configuradas
- O `DATABASE_URL` está correto

### Site não carrega?

- Verifique se `ALLOWED_HOSTS` inclui seu domínio do Render
- Verifique os logs em **"Logs"** no dashboard do Render

### Arquivos estáticos não aparecem?

- Certifique-se que o WhiteNoise está instalado
- Rode `python manage.py collectstatic` localmente para testar

## 📞 Suporte

Se tiver problemas, verifique:
- Logs do Render
- Documentação: https://render.com/docs
- Comunidade: https://community.render.com
