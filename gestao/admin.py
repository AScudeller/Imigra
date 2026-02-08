from django.contrib import admin
from .models import Cliente, Processo, Documento, Fatura, Parcela, Pagamento, AlocacaoPagamento, ModeloContrato, TipoVisto, EtapaPadrao, EtapaProcesso, Lead, Despesa

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
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
class ProcessoAdmin(admin.ModelAdmin):
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
class FaturaAdmin(admin.ModelAdmin):
    list_display = ('doc_entry', 'cliente', 'total_fatura', 'total_pago', 'status', 'imprimir_invoice')
    list_filter = ('status', 'data_fatura')
    search_fields = ('cliente__nome',)
    inlines = [ParcelaInline]

    def imprimir_invoice(self, obj):
        url = reverse('gerar_invoice_pdf', args=[obj.doc_entry])
        return format_html('<a class="button" href="{}" target="_blank" style="background:#447e9b; color:white; padding:5px 10px; border-radius:4px; text-decoration:none;">Imprimir PDF</a>', url)
    
    imprimir_invoice.short_description = "Ações"

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
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
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nome', 'interesse', 'status', 'criado_em')
    list_filter = ('status', 'interesse')
    search_fields = ('nome', 'email', 'telefone')

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data_vencimento', 'pago')
    list_filter = ('pago', 'categoria', 'data_vencimento')
    search_fields = ('descricao',)

# Personalização do Painel de Administração
admin.site.site_header = "G IMIGRA"
admin.site.site_title = "Painel Administrativo G IMIGRA"
admin.site.index_title = "Gestão de Imigração e Financeiro"
