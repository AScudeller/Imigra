# GUIA DE MIGRAÇÃO E CONFIGURAÇÃO DO SERVIDOR LOCAL
**Data:** 14/02/2026

Este guia descreve o passo a passo para configurar seu **NOVO SERVIDOR**, restaurar os sistemas e configurar o acesso externo via **Cloudflare Tunnel (Gratuito e Seguro)**.

---

## 🏗️ PARTE 1: Preparação do Novo Servidor (Hardware Limpo)

Antes de copiar os arquivos, instale os softwares necessários na nova máquina:

### 1. Instalar XAMPP (Para o PHP/MySQL)
*   Baixe e instale o **XAMPP** (versão com PHP 8.0 ou superior).
*   Instale preferencialmente no disco `C:\xampp`.
*   Abra o **XAMPP Control Panel** e inicie os serviços **Apache** e **MySQL**.
*   **Importante:** Clique em "Config" e marque para autoiniciar os serviços se o PC reiniciar.

### 2. Instalar Python (Para o Django)
*   Baixe o Python 3.12+ no site oficial.
*   **IMPORTANTE**: Na instalação, marque a opção **"Add Python to PATH"**.

### 3. Instalar Git (Opcional, mas recomendado)
*   Baixe e instale o Git for Windows.

---

## 📦 PARTE 2: Restaurar os Sistemas

Transfira a pasta `MIGRATION_PACKAGE` (gerada pelo script de backup na máquina antiga) para o novo servidor (ex: na Área de Trabalho ou em `C:\Sistemas`).

### 1. Restaurar Banco de Dados (MySQL)
1.  Abra o navegador no servidor e acesse: `http://localhost/phpmyadmin`
2.  Clique em **Importar** (menu superior).
3.  Selecione o arquivo `backup_erp_imigracao.sql` (que está na pasta do pacote) e execute.
4.  Repita o processo para o `backup_iamoveis_calculos.sql`.
    *   *Nota:* Se não importar, você pode abrir o arquivo `.sql` no Bloco de Notas, copiar tudo e colar na aba "SQL" do phpMyAdmin.

### 2. Restaurar o "IAMoveisCalculos" (PHP)
1.  Copie a pasta `IAMoveisCalculos_V3` de dentro do pacote de migração.
2.  Cole dentro da pasta `htdocs` do XAMPP (Geralmente `C:\xampp\htdocs`).
3.  Renomeie a pasta para `iamoveis` (para ficar fácil de acessar: `http://localhost/iamoveis`).
4.  Teste o acesso no navegador: `http://localhost/iamoveis`.
    *   *Se der erro de banco de dados, verifique o arquivo `configuracoes.php` ou `src/db.php` e garanta que a senha do banco está vazia (padrão XAMPP) ou correta.*

### 3. Restaurar o "ERP_imigracao" (Python/Django)
1.  Copie a pasta `ERP_imigracao` para um local definitivo (Ex: `C:\Sistemas\ERP_imigracao`).
2.  Abra o **Terminal (CMD ou PowerShell)** e navegue até a pasta:
    ```powershell
    cd C:\Sistemas\ERP_imigracao
    ```
3.  Crie o ambiente virtual:
    ```powershell
    python -m venv venv
    ```
4.  Ative o ambiente:
    ```powershell
    .\venv\Scripts\activate
    ```
5.  Instale as dependências:
    ```powershell
    pip install -r requirements.txt
    ```
6.  Rode as migrações finais:
    ```powershell
    python manage.py migrate
    ```
7.  Teste o servidor rodando:
    ```powershell
    python manage.py runserver 0.0.0.0:8000
    ```
8.  Acesse `http://localhost:8000` para ver se funcionou.

---

## 🌐 PARTE 3: Configurar Acesso Externo (Cloudflare Tunnel)

Esta é a solução para acessar de fora sem abrir portas no roteador.

### 1. Criar Conta Cloudflare
1.  Acesse [dash.cloudflare.com](https://dash.cloudflare.com/) e crie uma conta (é grátis).
2.  **Opção A (Se você tem um domínio próprio)**: Adicione o site no Cloudflare.
3.  **Opção B (Sem domínio)**: Use o "Quick Tunnels" (mais simples para testes, mas o link muda se reiniciar) ou registre um domínio barato. *Recomendado: Ter um domínio para fixar o nome.*

### 2. Instalar e Rodar o Tunnel (Windows)
1.  No Dashboard do Cloudflare, vá em **Zero Trust** -> **Networks** -> **Tunnels**.
2.  Clique em **Create a Tunnel**.
3.  Escolha um nome (ex: `servidor-casa`) e clique em **Save**.
4.  Escolha o OS **Windows**.
5.  Copie o comando que aparece (algo como `cloudflared.exe service install ...`).
6.  No seu Servidor, abra o PowerShell como **Administrador** e cole o comando.
7.  Isso instalará o serviço do Cloudflared que rodará sempre.

### 3. Configurar os "Public Hostnames"
No painel do Cloudflare (onde você criou o túnel), vá na aba **Public Hostnames** e adicione:

**Para o IAMoveis:**
*   **Subdomain**: `iamoveis` (ex: `iamoveis.seudominio.com`)
*   **Service**: `http://localhost:80` (A porta 80 é o padrão do Apache/XAMPP)

**Para o ERP Python:**
*   **Subdomain**: `erp` (ex: `erp.seudominio.com`)
*   **Service**: `http://localhost:8000`
    *   *Nota: O Django deve estar rodando sempre. Recomendo usar o NSSM ou Task Scheduler para rodar o Django como serviço no Windows.*

### 4. Rodar Django como Serviço (Opcional, mas recomendado)
Para não ter que deixar a janela preta do Django aberta:
1.  Baixe o **NSSM** (Non-Sucking Service Manager).
2.  Rode `nssm install DjangoERP`.
3.  No campo Path: selecione o `python.exe` do seu ambiente virtual (`.\venv\Scripts\python.exe`).
4.  No campo Arguments: `manage.py runserver 0.0.0.0:8000`.
5.  No campo Startup directory: a pasta do projeto.
6.  Clique "Install Service".

---

## 🔄 Dicas Extras
*   **IP Fixo no Servidor**: Configure um IP fixo na placa de rede do servidor (ex: `192.168.1.100`) dentro da sua rede local.
*   **Energia**: Configure a BIOS do servidor para "Power On" após queda de energia ("Restore on AC Power Loss").
