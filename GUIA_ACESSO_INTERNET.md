# 🌐 COMO COLOCAR SEU SISTEMA NA INTERNET (Cloudflare Tunnel)

Para acessar seu sistema de qualquer lugar do mundo (sem abrir portas no roteador), usaremos o **Cloudflare Tunnel**.

## 🚀 Opção 1: Acesso Rápido e Temporário (Sem Domínio)
Ideal para testar AGORA. O link muda toda vez que você reiniciar o computador.

1.  **No SERVIDOR (192.168.86.250)**, baixe o Cloudflared:
    *   Link: [https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe)
    *   Renomeie o arquivo baixado para `cloudflared.exe`.
    *   Coloque ele dentro da pasta `C:\Sistemas\ERP_imigracao`.

2.  Abra o CMD (Terminal) nessa pasta e rode:
    ```cmd
    cloudflared.exe tunnel --url http://localhost:8000
    ```

3.  Ele vai gerar um link aleatório (algo como `https://happy-mountain-123.trycloudflare.com`).
    *   Esse link é o seu ERP na internet!

---

## 🏆 Opção 2: Acesso Profissional (Link Fixo)
Para ter um link fixo (ex: `erp.suaempresa.com`), você precisa de um domínio (custa uns R$ 40/ano no Registro.br ou GoDaddy) e uma conta grátis na Cloudflare.

### Passo 1: Conta Cloudflare
1.  Crie uma conta em [https://dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up).
2.  Adicione seu domínio lá (você precisará mudar os DNS no lugar onde comprou o domínio).

### Passo 2: Criar o Túnel
1.  No painel da Cloudflare, vá em **Zero Trust** > **Networks** > **Tunnels**.
2.  Clique em **Create a Tunnel**.
3.  Escolha **Cloudflared** e dê um nome (ex: `servidor-escritorio`).
4.  Clique em **Save**.
5.  Ele vai mostrar um comando para instalar o agente ("Install and run a connector").
    *   Copie o comando para **Windows**.
6.  **No SERVIDOR**, abra o PowerShell como **Administrador** e cole esse comando.
    *   Isso instala o serviço que fica rodando para sempre.

### Passo 3: Criar os Links (Public Hostnames)
Ainda na tela do Túnel no site da Cloudflare, vá na aba **Public Hostnames** e clique em **Add Public Hostname**.

**Para o ERP (Django):**
*   **Subdomain:** `erp` (ex: `erp.seudominio.com`)
*   **Service:** `http://localhost:8000`

**Para o IAMoveis (PHP):**
*   **Subdomain:** `imoveis` (ex: `imoveis.seudominio.com`)
*   **Service:** `http://localhost:8090`

**Pronto!** Agora você acessa `erp.seudominio.com` de qualquer lugar.
