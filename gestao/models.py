from django.db import models
from .models_contracts import ModeloContrato
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from simple_history.models import HistoricalRecords

# --- CADASTRO MESTRE (Master Data) ---

class TipoVisto(models.Model):
    codigo = models.CharField(_("Código (ex: O-1, EB-2)"), max_length=20, unique=True)
    nome = models.CharField(_("Nome do Visto"), max_length=100)
    descricao = models.TextField(_("Descrição"), blank=True)
    taxa_uscis_padrao = models.DecimalField(_("Taxa USCIS Padrão (USD)"), max_digits=10, decimal_places=2, default=0.00)
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    class Meta:
        verbose_name = _("Tipo de Visto")
        verbose_name_plural = _("Tipos de Vistos")

class Lead(models.Model):
    """
    CRM Initial Contact (Pre-Client).
    """
    STATUS_LEAD = [
        ('NOVO', 'Novo Contato'),
        ('QUALIFICADO', 'Qualificado (Interessado)'),
        ('PROPOSTA', 'Proposta Enviada'),
        ('CONVERTIDO', 'Convertido em Cliente'),
        ('PERDIDO', 'Perdido'),
    ]
    nome = models.CharField(_("Nome"), max_length=150)
    email = models.EmailField(_("Email"), blank=True, null=True)
    telefone = models.CharField(_("Telefone"), max_length=20)
    interesse = models.ForeignKey(TipoVisto, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_LEAD, default='NOVO')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Lead: {self.nome} - {self.status}"

class EtapaPadrao(models.Model):
    """
    Template de etapas/checklist para cada tipo de visto.
    """
    tipo_visto = models.ForeignKey(TipoVisto, on_delete=models.CASCADE, related_name='etapas_padrao')
    ordem = models.PositiveIntegerField(_("Ordem"), default=1)
    titulo = models.CharField(_("Título da Etapa"), max_length=150)
    descricao = models.TextField(_("O que deve ser feito?"), blank=True)
    obrigatoria = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo_visto.codigo} - {self.titulo}"

    class Meta:
        verbose_name = _("Etapa Padrão (Template)")
        verbose_name_plural = _("Etapas Padrão (Templates)")
        ordering = ['tipo_visto', 'ordem']

class Cliente(models.Model):
    """
    Representa o Parceiro de Negócio (Master Data OCRD no SAP B1).
    """
    card_code = models.CharField(_("Código do Cliente"), max_length=20, unique=True, blank=True)
    nome = models.CharField(_("Nome Completo / Razão Social"), max_length=255)
    apelido = models.CharField(_("Nome Social / Fantasia"), max_length=255, blank=True)
    email = models.EmailField(_("E-mail"), unique=True)
    telefone = models.CharField(_("Telefone/WhatsApp"), max_length=30)
    
    # Dados de Imigração
    passaporte = models.CharField(_("Passaporte"), max_length=50, blank=True)
    data_nascimento = models.DateField(_("Data de Nascimento"), null=True, blank=True)
    nacionalidade = models.CharField(_("Nacionalidade"), max_length=100, default="Brasileira")
    
    # Endereços
    endereco_origem = models.TextField(_("Endereço no País de Origem"), blank=True)
    endereco_eua = models.TextField(_("Endereço nos EUA"), blank=True)
    
    # Financeiro
    saldo_atual = models.DecimalField(_("Saldo Atual (USD)"), max_digits=12, decimal_places=2, default=0.00)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.nome} ({self.card_code})"

    def save(self, *args, **kwargs):
        if not self.card_code:
            # Gera um código automático estilo SAP: C0001
            ultimo = Cliente.objects.all().order_by('id').last()
            if not ultimo:
                self.card_code = "C0001"
            else:
                self.card_code = f"C{str(ultimo.id + 1).zfill(4)}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")
        ordering = ['nome']

# --- GESTÃO DE CASOS (Case Management) ---

class Processo(models.Model):
    STATUS_CHOICES = [
        ('TRIAGEM', 'Em Triagem'),
        ('COLETA', 'Coleta de Documentos'),
        ('ANALISE', 'Análise Jurídica'),
        ('USCIS', 'Protocolado no USCIS'),
        ('RFE', 'Aguardando Evidências (RFE)'),
        ('APROVADO', 'Aprovado'),
        ('NEGADO', 'Negado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='processos')
    tipo_visto = models.ForeignKey(TipoVisto, on_delete=models.PROTECT, verbose_name=_("Tipo de Visto"))
    orcamento = models.ForeignKey('Orcamento', on_delete=models.SET_NULL, null=True, blank=True, 
                                   verbose_name=_("Orçamento Vinculado"), 
                                   help_text=_("Orçamento aprovado que originou este processo"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='TRIAGEM')
    num_recibo_uscis = models.CharField(_("Número do Recibo USCIS"), max_length=50, blank=True)
    data_protocolo = models.DateField(_("Data de Protocolo"), null=True, blank=True)
    observacoes = models.TextField(_("Observações"), blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Ao criar um processo, gera o checklist baseado nas Etapas Padrão
            etapas_modelo = self.tipo_visto.etapas_padrao.all()
            for modelo in etapas_modelo:
                EtapaProcesso.objects.create(
                    processo=self,
                    titulo=modelo.titulo,
                    descricao=modelo.descricao,
                    ordem=modelo.ordem
                )

    class Meta:
        verbose_name = _("Processo")
        verbose_name_plural = _("Processos")

class EtapaProcesso(models.Model):
    """
    O checklist real do processo de um cliente específico.
    """
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='etapas')
    ordem = models.PositiveIntegerField(default=1)
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    concluida = models.BooleanField(_("Concluída"), default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    responsavel = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if self.concluida and not self.data_conclusao:
            self.data_conclusao = timezone.now()
            # Notificar conclusão de etapa
            from .notifications import NotificacaoService
            msg = f"G IMIGRA: A etapa '{self.titulo}' do seu processo foi CONCLUÍDA com sucesso! ✅"
            NotificacaoService.enviar_whatsapp(self.processo.cliente, msg)
        
        super().save(*args, **kwargs)

    def __str__(self):
        status = "✅" if self.concluida else "⏳"
        return f"{status} {self.titulo}"

    class Meta:
        verbose_name = _("Etapa do Processo")
        verbose_name_plural = _("Checklist do Processo")
        ordering = ['ordem']

class Documento(models.Model):
    STATUS_DOC = [
        ('PENDENTE', 'Aguardando Envio'),
        ('REVISAO', 'Sob Revisão'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado / Pendente de Correção'),
    ]
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='documentos')
    etapa = models.ForeignKey('EtapaProcesso', on_delete=models.SET_NULL, null=True, blank=True, related_name='arquivos', verbose_name=_("Etapa Correspondente"))
    nome = models.CharField(_("Descrição do Documento"), max_length=255)
    arquivo = models.FileField(upload_to='documentos/processos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_DOC, default='PENDENTE')
    comentarios = models.TextField(_("Feedback / Observações"), blank=True)
    data_upload = models.DateTimeField(auto_now_add=True)
    validade = models.DateField(_("Data de Validade"), null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.nome} ({self.processo.cliente.nome})"

# --- PROPOSTAS E ORÇAMENTOS (Presales / Quotation) ---

class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('ENVIADO', 'Enviado ao Cliente'),
        ('ACEITO', 'Aceito (Gerar Fatura)'),
        ('REJEITADO', 'Rejeitado'),
    ]
    FREQ_CHOICES = [
        ('SEMANAL', 'Semanal'),
        ('QUINZENAL', 'Quinzenal'),
        ('MENSAL', 'Mensal'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    tipo_visto = models.ForeignKey(TipoVisto, on_delete=models.PROTECT)
    valor_total = models.DecimalField(_("Valor Total (USD)"), max_digits=12, decimal_places=2)
    entrada = models.DecimalField(_("Valor de Entrada (USD)"), max_digits=12, decimal_places=2, default=0.00)
    num_parcelas = models.PositiveIntegerField(_("Número de Parcelas"), default=1)
    frequencia = models.CharField(_("Frequência"), max_length=20, choices=FREQ_CHOICES, default='MENSAL')
    data_proposta = models.DateField(_("Data da Proposta"), auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RASCUNHO')
    observacoes = models.TextField(blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Orçamento #{self.id} - {self.cliente.nome} ({self.tipo_visto.codigo})"

    class Meta:
        verbose_name = _("Orçamento")
        verbose_name_plural = _("Orçamentos")

class OrcamentoParcela(models.Model):
    """Visualização prévia das parcelas antes de virar fatura real"""
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='parcelas_preview')
    num_parcela = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_vencimento = models.DateField()

    def __str__(self):
        return f"P{self.num_parcela} - {self.valor}"

# --- MOTOR FINANCEIRO (Financial Engine - SAP B1 Style) ---

class Fatura(models.Model):
    """
    A/R Invoice (OINV). Representa a cobrança total de um serviço.
    """
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('PARCIAL', 'Pago Parcialmente'),
        ('PAGO', 'Pago Totalmente'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='faturas')
    processo = models.ForeignKey(Processo, on_delete=models.SET_NULL, null=True, blank=True, related_name='faturas')
    
    doc_entry = models.AutoField(primary_key=True)
    data_fatura = models.DateField(_("Data da Fatura"), auto_now_add=True)
    total_fatura = models.DecimalField(_("Total da Fatura (USD)"), max_digits=12, decimal_places=2)
    total_pago = models.DecimalField(_("Total Pago (USD)"), max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(_("Status"), max_length=15, choices=STATUS_CHOICES, default='ABERTO')
    history = HistoricalRecords()
    
    def saldo_devedor(self):
        return self.total_fatura - self.total_pago

    def __str__(self):
        return f"Invoice #{self.doc_entry} - {self.cliente.nome}"

    class Meta:
        verbose_name = _("Fatura")
        verbose_name_plural = _("Faturas")

class Parcela(models.Model):
    """
    Invoice Installments (INV6). Controle fino de vencimentos.
    """
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE, related_name='parcelas')
    num_parcela = models.IntegerField(_("Nº Parcela"))
    data_vencimento = models.DateField(_("Data de Vencimento"))
    valor_parcela = models.DecimalField(_("Valor da Parcela (USD)"), max_digits=12, decimal_places=2)
    valor_pago = models.DecimalField(_("Valor Pago (USD)"), max_digits=12, decimal_places=2, default=0.00)
    
    def status(self):
        if self.valor_pago >= self.valor_parcela:
            return "PAGO"
        from django.utils import timezone
        if self.data_vencimento < timezone.now().date():
            return "ATRASADO"
        return "ABERTO"

    def saldo(self):
        return self.valor_parcela - self.valor_pago

    def __str__(self):
        return f"{self.fatura} - Parcela {self.num_parcela}"

    class Meta:
        verbose_name = _("Parcela")
        verbose_name_plural = _("Parcelas")
        ordering = ['data_vencimento']

class Pagamento(models.Model):
    """
    Incoming Payments (ORCT). Registro da entrada de dinheiro.
    """
    METODOS_PAGAMENTO = [
        ('ZELLE', 'Zelle'),
        ('WIRE', 'Wire Transfer'),
        ('CHECK', 'Check'),
        ('CASH', 'Cash'),
        ('CREDIT_CARD', 'Credit Card'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pagamentos')
    data_pagamento = models.DateField(_("Data do Pagamento"))
    valor_total = models.DecimalField(_("Valor Total Recebido (USD)"), max_digits=12, decimal_places=2)
    metodo = models.CharField(_("Método"), max_length=20, choices=METODOS_PAGAMENTO)
    referencia = models.CharField(_("Referência/Comprovante"), max_length=100, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from .services import FinanceiroService
            from .notifications import NotificacaoService
            FinanceiroService.processar_pagamento(self.id)
            NotificacaoService.notificar_pagamento_recebido(self)

    def __str__(self):
        return f"Pagamento {self.id} - {self.cliente.nome} - ${self.valor_total}"

class AlocacaoPagamento(models.Model):
    """
    Faz a ligação entre o Pagamento e a Parcela que ele está baixando (RCT2).
    """
    pagamento = models.ForeignKey(Pagamento, on_delete=models.CASCADE, related_name='alocacoes')
    parcela = models.ForeignKey(Parcela, on_delete=models.CASCADE, related_name='alocacoes')
    valor_alocado = models.DecimalField(_("Valor Alocado (USD)"), max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Alocação ${self.valor_alocado} para {self.parcela}"
class LogNotificacao(models.Model):
    TIPOS = [('EMAIL', 'E-mail'), ('WHATSAPP', 'WhatsApp')]
    STATUS_CONTROLE = [('PENDENTE', 'Pendente'), ('SUCESSO', 'Sucesso'), ('ERRO', 'Erro')]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificacoes')
    parcela = models.ForeignKey(Parcela, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    mensagem = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CONTROLE, default='PENDENTE')
    data_envio = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.tipo} - {self.cliente.nome} - {self.status}"

class Despesa(models.Model):
    """
    Accounts Payable (A/P). Gastos do escritório.
    """
    CAT_CHOICES = [
        ('ALUGUEL', 'Aluguel / Office'),
        ('SALARIO', 'Salários / Freelancers'),
        ('MARKETING', 'Marketing / Ads'),
        ('SOFTWARE', 'Software / Assinaturas'),
        ('TAXA', 'Taxas Governamentais Pagas'),
        ('OUTROS', 'Outros'),
    ]
    descricao = models.CharField(max_length=255)
    categoria = models.CharField(max_length=20, choices=CAT_CHOICES)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_vencimento = models.DateField()
    pago = models.BooleanField(default=False)
    data_pagamento = models.DateField(null=True, blank=True)
    comprovante = models.FileField(upload_to='comprovantes/despesas/', null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.descricao} - ${self.valor}"

    class Meta:
        verbose_name = _("Contas a Pagar")
        verbose_name_plural = _("Contas a Pagar")
