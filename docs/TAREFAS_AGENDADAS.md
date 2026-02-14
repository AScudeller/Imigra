# Configuração de Tarefas Agendadas (Cron Jobs)

## Comando: check_vencimentos

Este comando verifica vencimentos e envia notificações automáticas.

### Execução Manual
```bash
python manage.py check_vencimentos
```

### Agendar no Windows (Task Scheduler)

1. Abra o **Agendador de Tarefas** (Task Scheduler)
2. Clique em **Criar Tarefa Básica**
3. Nome: `ERP Imigração - Verificar Vencimentos`
4. Gatilho: **Diariamente** às **09:00**
5. Ação: **Iniciar um programa**
   - Programa: `C:\Users\ascud\OneDrive\Sistemas\ERP_imigracao\venv\Scripts\python.exe`
   - Argumentos: `manage.py check_vencimentos`
   - Iniciar em: `C:\Users\ascud\OneDrive\Sistemas\ERP_imigracao`

### Agendar no Linux (Crontab)

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa todo dia às 9h)
0 9 * * * cd /caminho/para/ERP_imigracao && /caminho/para/venv/bin/python manage.py check_vencimentos
```

### O que o comando faz:

1. **Parcelas Atrasadas**: Envia notificação imediata para clientes com parcelas vencidas
2. **Parcelas a Vencer (5 dias)**: Envia lembrete preventivo
3. **Documentos a Vencer (5 dias)**: Alerta sobre documentos próximos do vencimento

### Logs

Todas as notificações são registradas em `gestao_lognotificacao` para auditoria.
