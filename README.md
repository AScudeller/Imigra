# 🏗️ ERP MOVEIS - WORKSPACE PYTHON (SERVIDOR)

## ✅ Workspace Isolado Criado com Sucesso!

Este workspace foi criado **no servidor** (192.168.86.250) em:
```
\\servidor\Sistemas\ERP_PYTHON\
```

## 📂 Estrutura Criada

```
\\servidor\Sistemas\ERP_PYTHON\
├── .venv\                  ✅ Ambiente virtual Python criado
├── src\                    ✅ Código fonte
│   ├── core\               ✅ Lógica de negócio
│   ├── api\                ✅ Endpoints REST
│   ├── database\           ✅ Models e conexão
│   ├── templates\          ✅ Interface HTML
│   ├── static\             ✅ CSS/JS/Imagens
│   ├── utils\              ✅ Utilitários
│   └── modules\            ✅ Módulos do sistema
│       ├── vendas\
│       ├── estoque\
│       ├── producao\
│       ├── financeiro\
│       └── usuarios\
├── config\                 ✅ Configurações Django
├── logs\                   ✅ Logs do sistema
├── storage\                ✅ Uploads e backups
│   ├── uploads\
│   ├── backups\
│   └── temp\
├── tests\                  ✅ Testes automatizados
│   ├── unit\
│   ├── integration\
│   └── fixtures\
├── docs\                   ✅ Documentação
├── scripts\                ✅ Scripts de automação
├── requirements.txt        ✅ Dependências Python
├── .env.example            ✅ Template de configuração
├── .env                    ✅ Configuração ativa
└── .gitignore              ✅ Arquivos ignorados

```

## 🚀 Próximos Passos

### 1. Instalar Dependências (No Servidor)

Conecte-se ao servidor via RDP ou acesse remotamente e execute:

```batch
cd \\servidor\Sistemas\ERP_PYTHON
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 2. Inicializar Projeto Django

```batch
django-admin startproject config .
python manage.py inspectdb > src\database\models_auto.py
```

### 3. Iniciar Servidor

```batch
python manage.py runserver 0.0.0.0:8080
```

**Acesso:**
- Local (no servidor): http://localhost:8080
- LAN: http://192.168.86.250:8080

## 🔒 Segurança

- ✅ Workspace isolado do sistema PHP
- ✅ Banco de dados em modo Read-Only (DB_READ_ONLY=True)
- ✅ Porta 8080 (não conflita com PHP na porta 8090)
- ✅ Ambiente virtual isolado

## 📝 Configuração

Edite o arquivo `.env` para ajustar configurações:

```bash
# Banco de dados
DB_NAME=iamoveis_calculos
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1

# Modo Read-Only (protege produção)
DB_READ_ONLY=True  # Mude para False apenas em produção
```

## 📚 Documentação

Consulte os documentos de migração em:
```
\\servidor\Sistemas\iamoveis\
├── MIGRATION_EXECUTIVE_SUMMARY.md
├── MIGRATION_ROUTES_MAP.md
├── MIGRATION_PHASE3_DETAILED.md
├── MIGRATION_PHASE4_NETWORK.md
└── WORKSPACE_ISOLATED_ARCHITECTURE.md
```

---

**Status:** ✅ Workspace criado e pronto para uso  
**Localização:** Servidor 192.168.86.250  
**Data de Criação:** 14 de Fevereiro de 2026
