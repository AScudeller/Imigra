# G IMIGRA 🚀 - Immigration ERP & Case Management

O **G IMIGRA** é um sistema completo de gestão para escritórios de imigração, projetado com a robustez e arquitetura de um ERP profissional (inspirado em padrões SAP B1). O sistema integra o fluxo operacional de vistos americanos com um motor financeiro potente e um CRM estratégico.

## 🌟 Principais Funcionalidades

### 📋 Operacional e Workflows
- **Checklist Automatizado:** Cada tipo de visto (EB-2, O-1, L-1, etc.) possui seu próprio template de etapas. Ao criar um processo, o roteiro de tarefas é gerado automaticamente.
- **Gestão de Processos:** Acompanhamento de status desde a Triagem até o Protocolo no USCIS.
- **Vincular Documentos às Etapas:** Clareza total sobre quais arquivos resolvem quais fases do processo.

### 💰 Motor Financeiro (SAP Style)
- **A/R Invoices:** Sistema de faturamento com gestão de parcelas (Installments).
- **Alocação Inteligente:** Os pagamentos recebidos são alocados automaticamente às parcelas mais antigas em aberto (baixa automática).
- **Invoices em PDF:** Gerador de faturas profissionais prontas para envio.

### 🤝 CRM e Leads
- **Funil de Vendas:** Gestão de contatos interessados (Leads) antes da conversão em clientes.
- **Dashboard Gerencial:** Visão em tempo real do faturamento total, valores a receber e distribuição de casos por status.

### 👤 Portal do Cliente VIP
- **Transparência Total:** O cliente final possui um login exclusivo (via e-mail e passaporte).
- **Timeline de Progresso:** Visualização do checklist concluído pelo cliente.
- **Upload de Documentos:** O cliente pode enviar evidências diretamente pelo portal para revisão.

---

## 🛠️ Tecnologias Utilizadas
- **Backend:** Django (Python) 
- **DB:** SQLite (Desenvolvimento)
- **Frontend:** Bootstrap 5 & FontAwesome
- **PDF:** ReportLab
- **Segurança:** Sistema de permissões nativo do Django Admin

---

## 🚀 Como Executar

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Execute as migrações:**
   ```bash
   python manage.py migrate
   ```

3. **Inicie o servidor:**
   ```bash
   python manage.py runserver
   ```

4. **Scripts de Utilidade:**
   - `python generate_demo.py`: Gera dados de teste (Cliente, Processos, Leads e Faturas).
   - `python fix_accents.py`: Corrige automaticamente acentuação em checklists.

---

**Desenvolvido com foco em alta performance e organização imigratória. G IMIGRA - Elevando o padrão da sua advocacia.** 🇺🇸
