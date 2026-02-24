from django.contrib import admin
from .models import Cliente, Processo, Documento, Fatura, Parcela, Pagamento, AlocacaoPagamento, ModeloContrato, TipoVisto, EtapaPadrao, EtapaProcesso, Lead, Despesa, LogNotificacao, Orcamento, OrcamentoParcela
from simple_history.admin import SimpleHistoryAdmin
from django.utils.html import format_html
from django.urls import reverse

# --- INLINES GERAIS ---

class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 1
    fields = ('nome', 'arquivo', 'etapa', 'status', 'validade')

class EtapaProcessoInline(admin.TabularInline):
    model = EtapaProcesso
    extra = 0
    fields = ('ordem', 'titulo', 'concluida', 'data_conclusao')
    readonly_fields = ('data_conclusao',)

# --- FINANCEIRO INLINES ---

class FaturaClienteInline(admin.TabularInline):
    model = Fatura
    extra = 0
    can_delete = False
    fields = ('doc_entry', 'data_fatura', 'total_fatura', 'total_pago', 'status', 'imprimir_invoice')
    readonly_fields = ('doc_entry', 'data_fatura', 'total_fatura', 'total_pago', 'status', 'imprimir_invoice')
    show_change_link = True
    verbose_name = "Fatura / Invoice"
    verbose_name_plural = "Histórico de Faturas"

    def imprimir_invoice(self, obj):
        if not obj or not obj.doc_entry:
            return "-"
        url = reverse('gerar_invoice_pdf', args=[obj.doc_entry])
        return format_html('<a class="button" href="{}" target="_blank">Ver / Imprimir</a>', url)

class PagamentoClienteInline(admin.TabularInline):
    model = Pagamento
    extra = 0
    can_delete = False
    fields = ('id', 'data_pagamento', 'metodo', 'valor_total', 'referencia')
    readonly_fields = ('id', 'data_pagamento', 'metodo', 'valor_total', 'referencia')
    show_change_link = True
    verbose_name = "Pagamento Recebido"
    verbose_name_plural = "Histórico de Pagamentos"

class ParcelaInline(admin.TabularInline):
    model = Parcela
    extra = 0
    readonly_fields = ('valor_pago',)

class AlocacaoInline(admin.TabularInline):
    model = AlocacaoPagamento
    extra = 0
    readonly_fields = ('parcela', 'valor_alocado')
    can_delete = False

# --- CADASTROS PRINCIPAIS ---

@admin.register(Cliente)
class ClienteAdmin(SimpleHistoryAdmin):
    list_display = ('card_code', 'nome', 'email', 'telefone', 'saldo_atual_fmt')
    search_fields = ('card_code', 'nome', 'email', 'passaporte', 'endereco_eua')
    list_filter = ('nacionalidade',)
    readonly_fields = ('card_code', 'saldo_atual')
    inlines = [FaturaClienteInline, PagamentoClienteInline] # Painel Financeiro Integrado

    class Media:
        js = ('js/admin_masks.js',)

    def saldo_atual_fmt(self, obj):
        color = 'red' if obj.saldo_atual > 0 else 'green'
        return format_html('<span style="color: {}; font-weight: bold;">US$ {}</span>', color, obj.saldo_atual)
    saldo_atual_fmt.short_description = "Saldo Devedor (USD)"

@admin.register(Processo)
class ProcessoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'cliente', 'tipo_visto', 'orcamento_status', 'status', 'imprimir_contrato')
    list_filter = ('tipo_visto', 'status')
    search_fields = ('cliente__nome', 'num_recibo_uscis')
    inlines = [DocumentoInline, EtapaProcessoInline]
    raw_id_fields = ('orcamento',)
    
    def orcamento_status(self, obj):
        if obj.orcamento:
            color = 'green' if obj.orcamento.status == 'ACEITO' else 'orange'
            return format_html(
                '<span style="color: {}; font-weight: bold;">Orç #{} - {}</span>',
                color, obj.orcamento.id, obj.orcamento.get_status_display()
            )
        return format_html('<span style="color: red;">⚠️ Sem Orçamento</span>')
    orcamento_status.short_description = "Orçamento"

    def imprimir_contrato(self, obj):
        if not obj.orcamento:
            return format_html('<span style="color: #999;" title="Vincule um orçamento primeiro">⚠️ Sem Orçamento</span>')
        if obj.orcamento.status != 'ACEITO':
            return format_html('<span style="color: orange;" title="Aguardando aprovação">⏳ Orç. Pendente</span>')
        
        url = reverse('gerar_contrato_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank" style="background:#2dce89; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Gerar Contrato</a>', url)
    imprimir_contrato.short_description = "Ações"

@admin.register(ModeloContrato)
class ModeloContratoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'criado_em', 'atualizado_em')
    list_filter = ('ativo',)
    readonly_fields = ('criado_em', 'atualizado_em')

@admin.register(Fatura)
class FaturaAdmin(SimpleHistoryAdmin):
    list_display = ('doc_entry', 'cliente', 'total_fatura', 'total_pago', 'status', 'imprimir_invoice', 'acoes_financeiro')
    list_filter = ('status', 'data_fatura')
    search_fields = ('cliente__nome',)
    inlines = [ParcelaInline]
    actions = ['estornar_fatura_action']

    def imprimir_invoice(self, obj):
        url = reverse('gerar_invoice_pdf', args=[obj.doc_entry])
        return format_html('<a class="button" href="{}" target="_blank" style="background:#447e9b; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Ver / Imprimir</a>', url)
    imprimir_invoice.short_description = "Ações"

    def acoes_financeiro(self, obj):
        if obj.status == 'CANCELADO':
            return format_html('<span style="color: grey;">Cancelada</span>')
        
        url = reverse('estornar_fatura', args=[obj.doc_entry])
        return format_html(
            '<a class="button" href="{}" style="background:#f5365c; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;" onclick="return confirm(\'Deseja realmente ESTORNAR esta fatura? Isso reverterá o saldo do cliente e desalocará pagamentos.\')">Estornar (Void)</a>',
            url
        )
    acoes_financeiro.short_description = "Financeiro"

    def estornar_fatura_action(self, request, queryset):
        from .services import FinanceiroService
        sucesso_count = 0
        erro_msgs = []
        for fatura in queryset:
            sucesso, msg = FinanceiroService.estornar_fatura(fatura.doc_entry)
            if sucesso:
                sucesso_count += 1
            else:
                erro_msgs.append(msg)
        
        if sucesso_count:
            self.message_user(request, f"{sucesso_count} faturas estornadas com sucesso.")
        if erro_msgs:
            for msg in erro_msgs:
                self.message_user(request, msg, level='ERROR')
    estornar_fatura_action.short_description = "Estornar (Void) Invoices Selecionadas"

@admin.register(Pagamento)
class PagamentoAdmin(SimpleHistoryAdmin):
    change_list_template = 'gestao/admin/pagamento_change_list.html' # View Customizada
    list_display = ('id', 'cliente', 'valor_total', 'metodo', 'data_pagamento')
    list_filter = ('metodo', 'data_pagamento')
    search_fields = ('cliente__nome', 'referencia')
    inlines = [AlocacaoInline] # Auditoria de Alocação

# --- CADASTROS AUXILIARES ---

class EtapaPadraoInline(admin.TabularInline):
    model = EtapaPadrao
    extra = 3

@admin.register(TipoVisto)
class TipoVistoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome')
    search_fields = ('codigo', 'nome')
    inlines = [EtapaPadraoInline]

@admin.register(AlocacaoPagamento)
class AlocacaoPagamentoAdmin(admin.ModelAdmin):
    list_display = ('pagamento', 'parcela', 'valor_alocado')

@admin.register(Lead)
class LeadAdmin(SimpleHistoryAdmin):
    list_display = ('nome', 'interesse', 'status', 'criado_em')
    list_filter = ('status', 'interesse')
    search_fields = ('nome', 'email', 'telefone')

    class Media:
        js = ('js/admin_masks.js',)

@admin.register(Despesa)
class DespesaAdmin(SimpleHistoryAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data_vencimento', 'pago')
    list_filter = ('pago', 'categoria', 'data_vencimento')
    search_fields = ('descricao',)

@admin.register(LogNotificacao)
class LogNotificacaoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'cliente', 'tipo', 'status', 'data_envio')
    list_filter = ('tipo', 'status', 'data_envio')
    search_fields = ('cliente__nome', 'mensagem')
    readonly_fields = ('data_envio',)

# --- ORÇAMENTOS ---

class OrcamentoParcelaInline(admin.TabularInline):
    model = OrcamentoParcela
    extra = 0

@admin.register(Orcamento)
class OrcamentoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'cliente', 'tipo_visto', 'valor_total', 'status', 'imprimir_orcamento')
    list_filter = ('status', 'frequencia')
    search_fields = ('cliente__nome',)
    inlines = [OrcamentoParcelaInline]
    actions = ['converter_para_fatura', 'acao_gerar_plano']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Só gera parcelas automaticamente na CRIAÇÃO do orçamento
        # Na edição (change=True), preserva as parcelas que o usuário editou manualmente
        if not change:
            # Novo orçamento: gera o plano de pagamento automaticamente
            self.gerar_parcelas_orcamento(obj)
        else:
            # Edição: só gera se não existir nenhuma parcela ainda
            if obj.parcelas_preview.count() == 0:
                self.gerar_parcelas_orcamento(obj)

    def gerar_parcelas_orcamento(self, orc):
        """Gera parcelas preview - chamado apenas na criação ou ação manual"""
        if orc.valor_total <= 0: return
        from django.utils import timezone
        from decimal import Decimal
        from datetime import timedelta
        
        orc.parcelas_preview.all().delete()
        saldo = orc.valor_total - orc.entrada
        data_atual = timezone.now().date()
        
        if orc.num_parcelas >= 1:
            OrcamentoParcela.objects.create(orcamento=orc, num_parcela=1, valor=orc.entrada if orc.num_parcelas > 1 else orc.valor_total, data_vencimento=data_atual)
        
        num_restantes = orc.num_parcelas - 1
        if num_restantes > 0 and saldo > 0:
            valor_parcela = (saldo / num_restantes).quantize(Decimal('0.01'))
            for i in range(1, num_restantes + 1):
                days = 7 if orc.frequencia == 'SEMANAL' else 15 if orc.frequencia == 'QUINZENAL' else 30
                OrcamentoParcela.objects.create(orcamento=orc, num_parcela=i+1, valor=valor_parcela, data_vencimento=data_atual + timedelta(days=days*i))

    def acao_gerar_plano(self, request, queryset):
        """Ação manual para FORÇAR a regeração do plano de pagamento"""
        for orc in queryset:
            if orc.status != 'ACEITO': self.gerar_parcelas_orcamento(orc)
        self.message_user(request, "Plano de pagamento atualizado.")
    acao_gerar_plano.short_description = "Regerar Plano (apaga e recria as parcelas)"

    def imprimir_orcamento(self, obj):
        url = reverse('gerar_orcamento_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank" style="background:#5e72e4; color:white; padding:5px 10px; border-radius:4px;">Proposta PDF</a>', url)
    imprimir_orcamento.short_description = "Ações"

    def converter_para_fatura(self, request, queryset):
        for orc in queryset:
            if orc.status == 'ACEITO': continue
            if orc.parcelas_preview.count() == 0:
                 self.gerar_parcelas_orcamento(orc)
            
            fatura = Fatura.objects.create(cliente=orc.cliente, total_fatura=orc.valor_total, status='ABERTO')
            for preview in orc.parcelas_preview.all():
                Parcela.objects.create(fatura=fatura, num_parcela=preview.num_parcela, valor_parcela=preview.valor, data_vencimento=preview.data_vencimento)
            
            # Atualizar saldo devedor do cliente
            cliente = orc.cliente
            cliente.saldo_atual += orc.valor_total
            cliente.save()

            orc.status = 'ACEITO'
            orc.save()
        self.message_user(request, "Orçamentos convertidos em Faturas!")
    converter_para_fatura.short_description = "Converter para Fatura (Invoice)"
