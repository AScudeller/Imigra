# GUIA DE RESTAURAÇÃO (MÁQUINA NOVA)

Este guia explica exatamente como colocar seus sistemas para rodar no novo servidor.

---

## 🛑 IMPORTANTE:
Certifique-se que você já instalou na nova máquina:
1. **XAMPP** (Com Apache e MySQL rodando - Verdes no painel).
2. **Python** (Versão 3.10 ou superior).

---

## PASSO 1: Importar os Bancos de Dados (Sua dúvida principal)

Você tem dois arquivos `.sql` na pasta que extraiu: `backup_erp_imigracao.sql` e `backup_iamoveis_calculos.sql`.

1. Abra o navegador no novo servidor e acesse:
   👉 **http://localhost/phpmyadmin**

2. No menu superior, clique na aba **Importar** (Import).

3. Clique no botão **Escolher arquivo**.
   * Selecione o arquivo `backup_erp_imigracao.sql`.

4. Role a página até o final e clique no botão **Executar** (Import/Go).
   * *Aguarde a barra de progresso. Quando terminar, aparecerá uma faixa verde dizendo que a importação foi feita com sucesso.*

5. Repita o processo para o outro sistema:
   * Clique em **Importar** novamente.
   * Selecione o arquivo `backup_iamoveis_calculos.sql`.
   * Clique em **Executar**.

✅ **Pronto!** Seus dados antigos estão agora no banco de dados novo.

---

## PASSO 2: Configurar o Sistema PHP (IAMoveis)

1. Pegue a pasta `IAMoveisCalculos_V3` do seu pacote de migração.
2. Copie ela para dentro da pasta do XAMPP:
   👉 `C:\xampp\htdocs\`
3. Renomeie a pasta de `IAMoveisCalculos_V3` para apenas `iamoveis`.
4. Teste acessando: `http://localhost/iamoveis`

---

## PASSO 3: Configurar o Sistema Python (ERP)

1. Pegue a pasta `ERP_imigracao` do pacote.
2. Copie para um local fixo, ex: `C:\Sistemas\ERP_imigracao`.
3. Abra o prompt de comando (CMD) nessa pasta e rode:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py runserver
   ```
4. Teste acessando: `http://localhost:8000`

---

## PASSO 4: Liberar acesso externo (Gratuito)

Para acessar de fora da sua casa:

1. Baixe o **Cloudflared** (Google: "cloudflared download windows").
2. Abra o Prompt de Comando (CMD) como Administrador.
3. Rode o túnel para o sistema que você quer usar.

**Para o IAMoveis:**
`cloudflared tunnel --url http://localhost:80`

**Para o ERP Python:**
`cloudflared tunnel --url http://localhost:8000`

*O comando vai gerar um link aleatório (ex: `https://happy-mountain... trycloudflare.com`). Você pode usar esse link no celular (4G) para acessar seu sistema.*

*(Para um link fixo e profissional, siga as instruções de criar conta no site da Cloudflare que passei anteriormente).*
