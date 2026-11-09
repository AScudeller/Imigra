from django.contrib import admin, messages
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.html import format_html
from django.urls import reverse
from simple_history.admin import SimpleHistoryAdmin
import os

from .models import (Cliente, Processo, Documento, Fatura, Parcela, Pagamento, 
                     AlocacaoPagamento, ModeloContrato, TipoVisto, EtapaPadrao, 
                     EtapaProcesso, Lead, Despesa, LogNotificacao, Orcamento, 
                     OrcamentoParcela, AnexoCliente)
from .forms import AnexoClienteInlineForm, AnexoClienteAdminForm


def gerar_titulo_anexo(nome_arquivo, titulo_base='', total_arquivos=1):
    """
    Gera um título amigável para cada arquivo enviado em lote.
    - Se titulo_base estiver vazio, usa o nome limpo do próprio arquivo (sem extensão).
    - Se houver apenas 1 arquivo e titulo_base foi preenchido, usa titulo_base.
    - Se houver múltiplos arquivos e titulo_base foi preenchido, combina ambos.
    """
    base_name = os.path.basename(nome_arquivo or 'Arquivo')
    nome_sem_ext, _ = os.path.splitext(base_name)
    nome_limpo = nome_sem_ext.replace('_', ' ').strip() or base_name
    titulo_base = (titulo_base or '').strip()

    if not titulo_base:
        return nome_limpo
    if total_arquivos <= 1:
        return titulo_base
    return f"{titulo_base} - {nome_limpo}"


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

class AnexoClienteInline(admin.TabularInline):
    model = AnexoCliente
    form = AnexoClienteInlineForm
    extra = 1
    fields = ('preview_card', 'titulo', 'categoria', 'arquivo', 'observacoes')
    readonly_fields = ('preview_card',)
    verbose_name = "Anexo / Foto"
    verbose_name_plural = "📂 Anexos, Fotos e Documentos do Cliente"

    def preview_card(self, obj):
        if not obj or not obj.arquivo:
            return format_html(
                '<div style="text-align: center; padding: 4px;">'
                '<span style="display: inline-block; font-size: 20px; color: #94a3b8;">⬆️</span><br>'
                '<span style="font-size: 11px; color: #64748b; font-weight: 500;">Novo Envio (1 ou vários)</span>'
                '</div>'
            )
        
        if obj.is_image:
            media_html = format_html(
                '<a href="{}" target="_blank" title="Clique para ampliar em tamanho real">'
                '<img src="{}" class="anexo-thumb-img" alt="{}" />'
                '</a>',
                obj.arquivo.url, obj.arquivo.url, obj.titulo
            )
        elif obj.extensao == '.pdf':
            media_html = format_html(
                '<a href="{}" target="_blank" title="Abrir Documento PDF">'
                '<span class="anexo-doc-icon" style="color: #dc2626;">📄</span>'
                '</a>',
                obj.arquivo.url
            )
        else:
            media_html = format_html(
                '<a href="{}" target="_blank" title="Abrir Arquivo">'
                '<span class="anexo-doc-icon" style="color: #2563eb;">📁</span>'
                '</a>',
                obj.arquivo.url
            )

        return format_html(
            '<div class="anexo-thumb-container">'
            '  {}'
            '  <span class="anexo-file-meta">{} • {}</span>'
            '  <div class="anexo-btn-group">'
            '    <a class="btn-anexo-ver" href="{}" target="_blank" title="Visualizar">👁️ Ver</a>'
            '    <a class="btn-anexo-baixar" href="{}" download title="Baixar Arquivo">⬇️ Baixar</a>'
            '  </div>'
            '</div>',
            media_html, obj.tamanho_formatado, obj.extensao.upper() or 'ARQ', obj.arquivo.url, obj.arquivo.url
        )
    preview_card.short_description = "Visualização / Ações"

# --- CADASTROS PRINCIPAIS ---

@admin.register(AnexoCliente)
class AnexoClienteAdmin(SimpleHistoryAdmin):
    form = AnexoClienteAdminForm
    change_list_template = 'gestao/admin/anexocliente_change_list.html'
    change_form_template = 'gestao/admin/anexocliente_change_form.html'
    list_display = ('miniatura_preview', 'titulo', 'cliente', 'categoria', 'extensao_fmt', 'tamanho_formatado', 'data_upload', 'acoes')
    list_filter = ('categoria', 'data_upload', 'cliente')
    search_fields = ('titulo', 'cliente__nome', 'cliente__card_code', 'observacoes')

    class Media:
        css = {
            'all': ('css/anexos_admin.css',)
        }

    def get_fields(self, request, obj=None):
        if obj is None:
            # Na tela de Adicionar: oculta campos vazios de leitura (Preview, Data, Ações)
            return ('cliente', 'categoria', 'arquivo', 'titulo', 'observacoes')
        return ('cliente', 'categoria', 'titulo', 'arquivo', 'observacoes', 'miniatura_preview', 'data_upload', 'acoes')

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return ('miniatura_preview', 'data_upload', 'acoes')

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        cliente_id = request.GET.get('cliente')
        if cliente_id and not object_id:
            extra_context['cliente_pre_selecionado'] = Cliente.objects.filter(pk=cliente_id).first()
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        arquivos = request.FILES.getlist('arquivo')
        titulo_digitado = form.cleaned_data.get('titulo', '')

        if arquivos:
            total = len(arquivos)
            # Primeiro arquivo vai no objeto principal
            obj.arquivo = arquivos[0]
            obj.titulo = gerar_titulo_anexo(arquivos[0].name, titulo_digitado, total)
            super().save_model(request, obj, form, change)

            # Arquivos adicionais do lote (se o usuário selecionou 2 ou mais arquivos)
            for arq_extra in arquivos[1:]:
                AnexoCliente.objects.create(
                    cliente=obj.cliente,
                    titulo=gerar_titulo_anexo(arq_extra.name, titulo_digitado, total),
                    categoria=obj.categoria,
                    arquivo=arq_extra,
                    observacoes=obj.observacoes,
                )
            request._lote_anexos_qtd = total
            request._lote_anexos_cliente = obj.cliente
        else:
            if not obj.titulo and obj.arquivo:
                obj.titulo = gerar_titulo_anexo(obj.arquivo.name, '', 1)
            super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        qtd = getattr(request, '_lote_anexos_qtd', 1)
        cliente = getattr(request, '_lote_anexos_cliente', obj.cliente)

        if qtd > 1:
            self.message_user(
                request,
                f"✅ {qtd} arquivos foram anexados com sucesso na pasta do cliente {cliente.nome} ({cliente.card_code})!",
                level=messages.SUCCESS
            )
        if "_addanother" in request.POST:
            url = f"{reverse('admin:gestao_anexocliente_add')}?cliente={cliente.id}"
            return redirect(url)
        if "_continue" in request.POST:
            return super().response_add(request, obj, post_url_continue)
        # Redireciona para a tela agrupada direto na pasta do cliente
        url = f"{reverse('admin:gestao_anexocliente_changelist')}#cliente-{cliente.id}"
        return redirect(url)

    def response_change(self, request, obj):
        if "_continue" in request.POST or "_saveasnew" in request.POST or "_addanother" in request.POST:
            return super().response_change(request, obj)
        url = f"{reverse('admin:gestao_anexocliente_changelist')}#cliente-{obj.cliente_id}"
        return redirect(url)

    def changelist_view(self, request, extra_context=None):
        # Processamento de Upload Rápido Múltiplo direto da tela de Pastas por Cliente
        if request.method == 'POST' and request.POST.get('acao_upload_rapido') == '1':
            cliente_id = request.POST.get('cliente_id')
            categoria = request.POST.get('categoria', 'DOCUMENTO')
            titulo_base = request.POST.get('titulo', '').strip()
            observacoes = request.POST.get('observacoes', '').strip()
            arquivos = request.FILES.getlist('arquivos_lote')

            cliente = Cliente.objects.filter(pk=cliente_id).first()
            if not cliente:
                self.message_user(request, "⚠️ Selecione um cliente válido para anexar os arquivos.", level=messages.ERROR)
            elif not arquivos:
                self.message_user(request, "⚠️ Selecione pelo menos 1 arquivo para enviar.", level=messages.WARNING)
            else:
                total = len(arquivos)
                for arq in arquivos:
                    AnexoCliente.objects.create(
                        cliente=cliente,
                        titulo=gerar_titulo_anexo(arq.name, titulo_base, total),
                        categoria=categoria,
                        arquivo=arq,
                        observacoes=observacoes,
                    )
                self.message_user(
                    request,
                    f"✅ {total} arquivo(s) anexado(s) com sucesso para o cliente {cliente.nome} ({cliente.card_code})!",
                    level=messages.SUCCESS
                )
                return redirect(f"{reverse('admin:gestao_anexocliente_changelist')}#cliente-{cliente.id}")
            return redirect(reverse('admin:gestao_anexocliente_changelist'))

        # Filtros da visão agrupada por Cliente
        q = request.GET.get('q', '').strip()
        categoria_filtro = request.GET.get('categoria', '').strip()
        cliente_filtro = request.GET.get('cliente_id', '').strip()
        modo_visao = request.GET.get('visao', 'pastas').strip()

        anexos_qs = AnexoCliente.objects.select_related('cliente').order_by('-data_upload')
        if q:
            anexos_qs = anexos_qs.filter(
                Q(titulo__icontains=q) |
                Q(cliente__nome__icontains=q) |
                Q(cliente__card_code__icontains=q) |
                Q(observacoes__icontains=q) |
                Q(arquivo__icontains=q)
            )
        if categoria_filtro:
            anexos_qs = anexos_qs.filter(categoria=categoria_filtro)
        if cliente_filtro and cliente_filtro.isdigit():
            anexos_qs = anexos_qs.filter(cliente_id=int(cliente_filtro))

        # Agrupar anexos por Cliente mantendo cada qual com o seu cliente
        grupos_dict = {}
        for anexo in anexos_qs:
            cid = anexo.cliente_id
            if cid not in grupos_dict:
                grupos_dict[cid] = {
                    'cliente': anexo.cliente,
                    'anexos': [],
                    'total_anexos': 0,
                    'total_fotos': 0,
                    'total_docs': 0,
                    'ultimo_upload': anexo.data_upload,
                }
            grupo = grupos_dict[cid]
            grupo['anexos'].append(anexo)
            grupo['total_anexos'] += 1
            if anexo.is_image:
                grupo['total_fotos'] += 1
            else:
                grupo['total_docs'] += 1

        # Se filtrou por um cliente específico que ainda não tem anexos, exibe a pasta vazia dele para facilitar o envio
        if cliente_filtro and cliente_filtro.isdigit() and int(cliente_filtro) not in grupos_dict:
            cli_obj = Cliente.objects.filter(pk=int(cliente_filtro)).first()
            if cli_obj:
                grupos_dict[cli_obj.id] = {
                    'cliente': cli_obj,
                    'anexos': [],
                    'total_anexos': 0,
                    'total_fotos': 0,
                    'total_docs': 0,
                    'ultimo_upload': None,
                }

        # Ordena as pastas por nome do cliente
        grupos_clientes = sorted(grupos_dict.values(), key=lambda g: g['cliente'].nome.lower())

        extra_context = extra_context or {}
        extra_context.update({
            'grupos_clientes': grupos_clientes,
            'total_arquivos_geral': sum(g['total_anexos'] for g in grupos_clientes),
            'total_clientes_com_anexos': len(grupos_clientes),
            'todos_clientes': Cliente.objects.all().order_by('nome'),
            'categorias_choices': AnexoCliente.CATEGORIAS,
            'q_atual': q,
            'categoria_atual': categoria_filtro,
            'cliente_id_atual': int(cliente_filtro) if (cliente_filtro and cliente_filtro.isdigit()) else '',
            'modo_visao': modo_visao,
        })
        return super().changelist_view(request, extra_context=extra_context)

    def miniatura_preview(self, obj):
        if not obj or not obj.arquivo:
            return "-"
        if obj.is_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="width: 36px; height: 36px; object-fit: cover; border-radius: 4px;" />'
                '</a>',
                obj.arquivo.url, obj.arquivo.url
            )
        return format_html('<span>{}</span>', obj.extensao.upper() or 'ARQUIVO')
    miniatura_preview.short_description = "Preview"

    def extensao_fmt(self, obj):
        return obj.extensao.upper() or "-"
    extensao_fmt.short_description = "Formato"

    def acoes(self, obj):
        if not obj or not obj.arquivo:
            return "-"
        return format_html(
            '<a class="button" href="{}" target="_blank" style="margin-right: 5px; background: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; text-decoration: none;">👁️ Ver</a>'
            '<a class="button" href="{}" download style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; text-decoration: none;">⬇️ Baixar</a>',
            obj.arquivo.url, obj.arquivo.url
        )
    acoes.short_description = "Ações"


@admin.register(Cliente)
class ClienteAdmin(SimpleHistoryAdmin):
    list_display = ('card_code', 'nome', 'email', 'telefone', 'total_anexos_fmt', 'saldo_atual_fmt')
    search_fields = ('card_code', 'nome', 'email', 'passaporte', 'endereco_eua')
    list_filter = ('nacionalidade',)
    readonly_fields = ('card_code', 'saldo_atual')
    inlines = [AnexoClienteInline, FaturaClienteInline, PagamentoClienteInline] # Painel de Anexos + Financeiro Integrado

    def save_formset(self, request, form, formset, change):
        if formset.model == AnexoCliente:
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()

            saved_instances = set()
            for inline_form in formset.forms:
                if not inline_form.has_changed() or inline_form in formset.deleted_forms:
                    continue
                instance = inline_form.instance
                if not instance.cliente_id:
                    instance.cliente = form.instance

                file_field_name = inline_form.add_prefix('arquivo')
                uploaded_files = request.FILES.getlist(file_field_name)
                titulo_digitado = inline_form.cleaned_data.get('titulo', '')

                if len(uploaded_files) >= 1:
                    total = len(uploaded_files)
                    instance.arquivo = uploaded_files[0]
                    instance.titulo = gerar_titulo_anexo(uploaded_files[0].name, titulo_digitado, total)
                    instance.save()
                    saved_instances.add(instance.pk)

                    # Se o usuário selecionou múltiplos arquivos na mesma linha do inline, cria os demais automaticamente
                    for extra_f in uploaded_files[1:]:
                        AnexoCliente.objects.create(
                            cliente=form.instance,
                            titulo=gerar_titulo_anexo(extra_f.name, titulo_digitado, total),
                            categoria=instance.categoria,
                            arquivo=extra_f,
                            observacoes=instance.observacoes,
                        )
                elif instance.arquivo:
                    if not instance.titulo:
                        instance.titulo = gerar_titulo_anexo(instance.arquivo.name, '', 1)
                    instance.save()
                    saved_instances.add(instance.pk)

            for inst in instances:
                if inst.pk not in saved_instances and inst.arquivo:
                    if not inst.titulo:
                        inst.titulo = gerar_titulo_anexo(inst.arquivo.name, '', 1)
                    inst.save()
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)

    def total_anexos_fmt(self, obj):
        total = obj.anexos.count()
        url_pasta = f"{reverse('admin:gestao_anexocliente_changelist')}?cliente_id={obj.id}#cliente-{obj.id}"
        url_add = f"{reverse('admin:gestao_anexocliente_add')}?cliente={obj.id}"
        if total > 0:
            return format_html(
                '<div style="display: flex; gap: 5px; align-items: center; flex-wrap: nowrap;">'
                '<a href="{}" style="background: #28a745; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px; text-decoration: none; white-space: nowrap;" title="Ver pasta de arquivos deste cliente">📁 {} anexo(s)</a>'
                '<a href="{}" style="background: #2563eb; color: white; padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 11px; text-decoration: none; white-space: nowrap;" title="Anexar vários arquivos para este cliente">+ Anexar</a>'
                '</div>',
                url_pasta, total, url_add
            )
        return format_html(
            '<a href="{}" style="background: #2563eb; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-decoration: none; white-space: nowrap;" title="Anexar arquivos para este cliente">+ Anexar Arquivos</a>',
            url_add
        )
    total_anexos_fmt.short_description = "Anexos / Fotos"

    class Media:
        js = ('js/admin_masks.js',)
        css = {
            'all': ('css/anexos_admin.css',)
        }

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
