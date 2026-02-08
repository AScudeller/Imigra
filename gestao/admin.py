from django.contrib import admin
from .models import Cliente, Processo, Documento, Fatura, Parcela, Pagamento, AlocacaoPagamento, ModeloContrato, TipoVisto, EtapaPadrao, EtapaProcesso, Lead, Despesa, LogNotificacao, Orcamento, OrcamentoParcela
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Cliente)
class ClienteAdmin(SimpleHistoryAdmin):
    list_display = ('card_code', 'nome', 'email', 'telefone', 'saldo_atual')
    search_fields = ('card_code', 'nome', 'email', 'passaporte')
    list_filter = ('nacionalidade',)
    readonly_fields = ('card_code', 'saldo_atual')

class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 1
    fields = ('nome', 'arquivo', 'etapa', 'status', 'validade')

class EtapaProcessoInline(admin.TabularInline):
    model = EtapaProcesso
    extra = 0
    fields = ('ordem', 'titulo', 'concluida', 'data_conclusao')
    readonly_fields = ('data_conclusao',)

@admin.register(Processo)
class ProcessoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'cliente', 'tipo_visto', 'status', 'imprimir_contrato')
    list_filter = ('tipo_visto', 'status')
    search_fields = ('cliente__nome', 'num_recibo_uscis')
    inlines = [DocumentoInline, EtapaProcessoInline]

    def imprimir_contrato(self, obj):
        url = reverse('gerar_contrato_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank" style="background:#5e72e4; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Gerar Contrato</a>', url)
    
    imprimir_contrato.short_description = "Ações"

@admin.register(ModeloContrato)
class ModeloContratoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_visto', 'ativo')

from django.utils.html import format_html
from django.urls import reverse

class ParcelaInline(admin.TabularInline):
    model = Parcela
    extra = 0
    readonly_fields = ('valor_pago',)

@admin.register(Fatura)
class FaturaAdmin(SimpleHistoryAdmin):
    list_display = ('doc_entry', 'cliente', 'total_fatura', 'total_pago', 'status', 'imprimir_invoice')
    list_filter = ('status', 'data_fatura')
    search_fields = ('cliente__nome',)
    inlines = [ParcelaInline]

    def imprimir_invoice(self, obj):
        url = reverse('gerar_invoice_pdf', args=[obj.doc_entry])
        return format_html('<a class="button" href="{}" target="_blank" style="background:#447e9b; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Imprimir PDF</a>', url)
    
    imprimir_invoice.short_description = "Ações"

@admin.register(Pagamento)
class PagamentoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'cliente', 'valor_total', 'metodo', 'data_pagamento')
    list_filter = ('metodo', 'data_pagamento')
    search_fields = ('cliente__nome', 'referencia')

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

class OrcamentoParcelaInline(admin.TabularInline):
    model = OrcamentoParcela
    extra = 0
    readonly_fields = ('num_parcela', 'valor', 'data_vencimento')

@admin.register(Orcamento)
class OrcamentoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'cliente', 'tipo_visto', 'valor_total', 'status', 'imprimir_orcamento')
    list_filter = ('status', 'frequencia')
    search_fields = ('cliente__nome',)
    inlines = [OrcamentoParcelaInline]
    actions = ['gerar_plano_pagamento', 'converter_para_fatura']

    def imprimir_orcamento(self, obj):
        url = reverse('gerar_orcamento_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank" style="background:#5e72e4; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Imprimir Proposta</a>', url)
    
    imprimir_orcamento.short_description = "Ações"

    def gerar_plano_pagamento(self, request, queryset):
        from datetime import timedelta
        for orc in queryset:
            # Limpa prévias antigas
            orc.parcelas_preview.all().delete()
            
            saldo = orc.valor_total - orc.entrada
            data_atual = timezone.now().date()
            
            # 1. Entrada (se houver)
            if orc.entrada > 0:
                OrcamentoParcela.objects.create(
                    orcamento=orc, num_parcela=0, valor=orc.entrada, data_vencimento=data_atual
                )
            
            # 2. Parcelas
            if orc.num_parcelas > 0:
                valor_parcela = (saldo / orc.num_parcelas).quantize(Decimal('0.01'))
                
                for i in range(1, orc.num_parcelas + 1):
                    if orc.frequencia == 'SEMANAL':
                        data_venc = data_atual + timedelta(weeks=i)
                    elif orc.frequencia == 'QUINZENAL':
                        data_venc = data_atual + timedelta(days=15 * i)
                    else: # MENSAL
                        # Aproximação simples de mês (30 dias) ou usar relativedelta para precisão SAP
                        data_venc = data_atual + timedelta(days=30 * i)
                        
                    OrcamentoParcela.objects.create(
                        orcamento=orc, num_parcela=i, valor=valor_parcela, data_vencimento=data_venc
                    )
        self.message_user(request, "Plano de pagamento gerado com sucesso!")

    def converter_para_fatura(self, request, queryset):
        for orc in queryset:
            if orc.parcelas_preview.count() == 0:
                self.message_user(request, f"Erro: Orçamento {orc.id} não possui plano de pagamento gerado.", level='ERROR')
                continue
            
            # Criar Fatura (Invoice)
            fatura = Fatura.objects.create(
                cliente=orc.cliente,
                total_fatura=orc.valor_total,
                status='ABERTO'
            )
            
            # Criar Parcelas Reais
            for preview in orc.parcelas_preview.all():
                Parcela.objects.create(
                    fatura=fatura,
                    num_parcela=preview.num_parcela if preview.num_parcela > 0 else 1,
                    valor_parcela=preview.valor,
                    data_vencimento=preview.data_vencimento
                )
            
            orc.status = 'ACEITO'
            orc.save()
            
        self.message_user(request, "Orçamentos convertidos em Invoices com sucesso!")

# Personalização do Painel de Administração
admin.site.site_header = "G IMIGRA"
admin.site.site_title = "Painel Administrativo G IMIGRA"
admin.site.index_title = "Gestão de Imigração e Financeiro"
