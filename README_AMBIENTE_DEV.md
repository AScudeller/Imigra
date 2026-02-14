# Configuração do Ambiente de Desenvolvimento Local

Como você transferiu os arquivos e o banco de dados para o servidor (192.168.86.250), mas quer programar e rodar o sistema da sua máquina local, eu criei scripts para facilitar isso.

## 🛠️ Passo 1: Configurar Dependências

Execute o arquivo:
`SETUP_LOCAL_DEV.bat`

Isso fará:
1.  Criará um ambiente virtual Python (`venv_dev`) na pasta do projeto.
2.  Instalará todas as bibliotecas necessárias.
3.  Tentará configurar o banco de dados localmente.

## 🚀 Passo 2: Rodar os Servidores

Para iniciar o Django (ERP) e o PHP (IAMoveis) ao mesmo tempo, execute:
`RUN_LOCAL_APP.bat`

Isso abrirá duas janelas:
1.  **ERP Imigração (Django)**: Acessível em [http://localhost:8000](http://localhost:8000)
2.  **IAMoveis (PHP)**: Acessível em [http://localhost:8090](http://localhost:8090)

---

## ⚠️ Sobre o Banco de Dados

Atualmente, o sistema está configurado para conectar em **`localhost` (127.0.0.1)**.
Isso significa que quando você roda o sistema na sua máquina, ele tenta conectar no **SEU banco de dados local**, e não no do servidor.

Se você tiver o MySQL instalado localmente (XAMPP), o sistema funcionará, mas os dados estarão vazios ou desatualizados em relação ao servidor.

### Opção A: Usar Banco Local (Recomendado para Desenvolvimento)
Se quiser usar o banco local, certifique-se de importar os arquivos `.sql` que estão na pasta raiz (`banco_erp_imigracao.sql` e `banco_iamoveis.sql`) para o seu MySQL local (usando phpMyAdmin ou Workbench).

### Opção B: Conectar no Banco do Servidor (192.168.86.250)
Se quiser que sua máquina conecte diretamente no banco do servidor, você precisará:
1.  No Servidor, abrir o MySQL e permitir conexões externas.
2.  Rodar o comando SQL no servidor:
    ```sql
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '';
    FLUSH PRIVILEGES;
    ```
3.  Alterar as configurações dos sistemas (`settings.py` e `db.php`) para apontar para `192.168.86.250`.
    *   **Atenção:** Isso deixará o banco exposto na rede local.

Se tiver dúvidas, pode seguir com a **Opção A** que é mais simples e segura.
