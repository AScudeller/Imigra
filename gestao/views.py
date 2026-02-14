from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Cliente, Processo, Fatura, Parcela, Pagamento, TipoVisto, Lead, Documento, EtapaProcesso
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse
from django.contrib import messages
from decimal import Decimal
import os
import zipfile
import subprocess
import io

@login_required
def dashboard(request):
    hoje = timezone.now().date()
    # KPIs Financeiros
    total_faturado = Fatura.objects.exclude(status='CANCELADO').aggregate(Sum('total_fatura'))['total_fatura__sum'] or 0
    total_recebido = Pagamento.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    total_a_receber = Parcela.objects.filter(valor_pago__lt=F('valor_parcela')).aggregate(total=Sum(F('valor_parcela') - F('valor_pago')))['total'] or 0
    total_atrasado = Parcela.objects.filter(data_vencimento__lt=hoje, valor_pago__lt=F('valor_parcela')).aggregate(total=Sum(F('valor_parcela') - F('valor_pago')))['total'] or 0
    
    # KPIs CRM
    total_leads = Lead.objects.count()
    leads_novos = Lead.objects.filter(status='NOVO').count()
    
    # Alertas Proativos (Próximos 5 dias)
    alerta_data = hoje + timezone.timedelta(days=5)
    parcelas_alerta = Parcela.objects.filter(data_vencimento__lte=alerta_data, valor_pago__lt=F('valor_parcela')).exclude(fatura__status='CANCELADO').order_by('data_vencimento')
    docs_alerta = Documento.objects.filter(validade__lte=alerta_data).order_by('validade')
    
    context = {
        'total_faturado': total_faturado,
        'total_recebido': total_recebido,
        'total_a_receber': total_a_receber,
        'total_atrasado': total_atrasado,
        'total_leads': total_leads,
        'leads_novos': leads_novos,
        'processos_por_status': Processo.objects.values('status').annotate(total=Count('id')),
        'todos_vistos': TipoVisto.objects.all(),
        'parcelas_alerta': parcelas_alerta,
        'docs_alerta': docs_alerta,
        'ultimos_pagamentos': Pagamento.objects.all().order_by('-data_pagamento')[:5],
        'ultimos_clientes': Cliente.objects.all().order_by('-id')[:6],
        'total_processos': Processo.objects.count(),
    }
    return render(request, 'gestao/dashboard.html', context)

def cliente_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        passaporte = request.POST.get('passaporte')
        cliente = Cliente.objects.filter(email=email, passaporte=passaporte).first()
        if cliente:
            request.session['cliente_id'] = cliente.id
            return redirect('cliente_portal')
    return render(request, 'gestao/portal_login.html')

def cliente_portal(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('cliente_login')
    
    cliente = Cliente.objects.get(id=cliente_id)
    
    if request.method == 'POST' and request.FILES.get('arquivo'):
        processo_id = request.POST.get('processo_id')
        etapa_id = request.POST.get('etapa_id')
        processo = get_object_or_404(Processo, id=processo_id, cliente=cliente)
        etapa = EtapaProcesso.objects.filter(id=etapa_id, processo=processo).first()
        
        Documento.objects.create(
            processo=processo,
            etapa=etapa,
            nome=request.POST.get('nome', 'Upload via Portal'),
            arquivo=request.FILES.get('arquivo'),
            status='REVISAO'
        )
        return redirect('cliente_portal')

    processos = cliente.processos.all()
    faturas = cliente.faturas.all()
    orcamentos = cliente.orcamentos.all().order_by('-data_proposta')
    
    return render(request, 'gestao/portal_cliente.html', {
        'cliente': cliente,
        'processos': processos,
        'faturas': faturas,
        'orcamentos': orcamentos,
    })

# --- GESTÃO FINANCEIRA AVANÇADA (Contas a Receber) ---
from django.http import JsonResponse
from django.contrib import messages
from .forms import PagamentoForm, FiltroParcelasForm
from .services import FinanceiroService

@login_required
def baixa_pagamento_view(request):
    """
    Tela principal de Baixa de Pagamentos (Contas a Receber).
    """
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        
        if form.is_valid():
            try:
                # 1. Salvar o Pagamento (Header)
                pagamento = form.save(commit=False)
                # Se o valor total vier zerado do form (readonly), pega do request manual ou recalcula
                valor_total_form = form.cleaned_data['valor_total']
                
                # Coletar parcelas selecionadas do POST
                parcelas_ids = request.POST.getlist('parcelas_selecionadas')
                dados_baixa = []
                total_calculado = Decimal('0.00')
                
                for pid in parcelas_ids:
                    # Valor digitado pelo usuário para esta parcela
                    val_str = request.POST.get(f'valor_pagar_{pid}')
                    if val_str:
                        val = Decimal(val_str)
                        if val > 0:
                            dados_baixa.append({'id': pid, 'valor': val})
                            total_calculado += val
                
                # Se usuário não informou total (campo readonly), usa o calculado
                if not valor_total_form or valor_total_form == 0:
                    pagamento.valor_total = total_calculado
                else:
                    pagamento.valor_total = valor_total_form
                
                pagamento.save()
                
                # 2. Processar Baixa (Alocação)
                if dados_baixa:
                    FinanceiroService.processar_pagamento_manual(pagamento.id, dados_baixa)
                else:
                    # Se não selecionou nada mas salvou pagamento "Avulso" (Adiantamento)
                    pass 
                
                messages.success(request, f"Pagamento #{pagamento.id} registrado com sucesso! Valor: ${pagamento.valor_total}")
                return redirect('admin:gestao_pagamento_changelist')
            
            except Exception as e:
                messages.error(request, f"Erro ao processar baixa: {str(e)}")
    else:
        form = PagamentoForm()
    
    filtro_form = FiltroParcelasForm()

    return render(request, 'gestao/admin/baixa_pagamento.html', {
        'form': form,
        'filtro_form': filtro_form,
        'opts': Pagamento._meta, # Para o admin template saber titulo etc
        'has_permission': True,
        'site_title': 'ERP Imigração',
        'site_header': 'ERP Imigração',
    })

@login_required
def api_parcelas_cliente(request):
    """
    Retorna JSON com parcelas em aberto para o cliente selecionado.
    """
    cliente_id = request.GET.get('cliente_id')
    data_ini = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status_filter = request.GET.get('status', 'ABERTO')
    
    if not cliente_id:
        return JsonResponse({'parcelas': []})
    
    qs = Parcela.objects.filter(fatura__cliente_id=cliente_id)
    
    # Filtro Status
    if status_filter == 'ABERTO':
        qs = qs.filter(valor_pago__lt=F('valor_parcela'))
    
    # Filtro Data
    if data_ini:
        qs = qs.filter(data_vencimento__gte=data_ini)
    if data_fim:
        qs = qs.filter(data_vencimento__lte=data_fim)
        
    qs = qs.order_by('data_vencimento', 'fatura_id', 'num_parcela')
    
    data = []
    hoje = timezone.now().date()
    
    for p in qs:
        saldo = p.valor_parcela - p.valor_pago
        atrasado = (p.data_vencimento < hoje) and (saldo > 0)
        
        data.append({
            'id': p.id,
            'fatura_id': p.fatura.doc_entry,
            'num_parcela': p.num_parcela,
            'vencimento_fmt': p.data_vencimento.strftime('%d/%m/%Y'),
            'valor_total_fmt': f"{p.valor_parcela:,.2f}",
            'saldo': float(saldo),
            'saldo_fmt': f"{saldo:,.2f}",
            'atrasado': atrasado
        })
        
    return JsonResponse({'parcelas': data})

@login_required
def relatorio_inadimplencia_view(request):
    """
    Relatório de Inadimplência (Aging Report).
    Agrupa contas a receber por faixas de atraso.
    """
    hoje = timezone.now().date()
    
    # 1. Buscar todas as parcelas em aberto com saldo > 0
    parcelas = Parcela.objects.filter(valor_pago__lt=F('valor_parcela')).select_related('fatura__cliente')
    
    clientes_map = {}
    
    total_adimplente = Decimal('0.00')
    total_30 = Decimal('0.00')
    total_60_plus = Decimal('0.00') # Soma de 30-60, 60-90, >90
    total_geral_devido = Decimal('0.00')

    for p in parcelas:
        cliente_id = p.fatura.cliente.id
        nome_cliente = p.fatura.cliente.nome
        email_cliente = p.fatura.cliente.email
        
        saldo = p.valor_parcela - p.valor_pago
        dias_atraso = (hoje - p.data_vencimento).days
        
        if cliente_id not in clientes_map:
            clientes_map[cliente_id] = {
                'cliente_id': cliente_id,
                'nome': nome_cliente,
                'email': email_cliente,
                'current': Decimal('0.00'), # A vencer
                'd30': Decimal('0.00'),     # 1-30 dias
                'd60': Decimal('0.00'),     # 31-60 dias
                'd90': Decimal('0.00'),     # 61-90 dias
                'd90_plus': Decimal('0.00'),# > 90 dias
                'total': Decimal('0.00')
            }
            
        dados = clientes_map[cliente_id]
        dados['total'] += saldo
        total_geral_devido += saldo
        
        if dias_atraso <= 0:
            dados['current'] += saldo
            total_adimplente += saldo
        else:
            if dias_atraso <= 30:
                dados['d30'] += saldo
                total_30 += saldo
            elif dias_atraso <= 60:
                dados['d60'] += saldo
                total_60_plus += saldo
            elif dias_atraso <= 90:
                dados['d90'] += saldo
                total_60_plus += saldo
            else:
                dados['d90_plus'] += saldo
                total_60_plus += saldo
    
    # Ordenar por maior dívida total
    lista_clientes = sorted(clientes_map.values(), key=lambda x: x['total'], reverse=True)
    
    return render(request, 'gestao/admin/relatorio_inadimplencia.html', {
        'dados_clientes': lista_clientes,
        'total_adimplente': total_adimplente,
        'total_30': total_30,
        'total_60_plus': total_60_plus,
        'total_geral_devido': total_geral_devido,
        'site_title': 'Relatório Financeiro',
        'site_header': 'ERP Imigração',
        'has_permission': True,
    })

# --- EDITOR DE CONTRATO ÚNICO ---

@login_required
def editor_contrato_unico_view(request):
    """
    Editor do contrato padrão único (serve para todos os tipos de visto).
    """
    from .models_contracts import ModeloContrato
    
    # Buscar o contrato ativo (deve haver apenas 1)
    contrato = ModeloContrato.objects.filter(ativo=True).first()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        conteudo = request.POST.get('conteudo')
        ativo = request.POST.get('ativo') == 'on'
        
        if contrato:
            # Atualizar existente
            contrato.nome = nome
            contrato.conteudo = conteudo
            contrato.ativo = ativo
            contrato.save()
            messages.success(request, 'Contrato atualizado com sucesso!')
        else:
            # Criar novo
            contrato = ModeloContrato.objects.create(
                nome=nome,
                conteudo=conteudo,
                ativo=ativo
            )
            messages.success(request, 'Contrato criado com sucesso!')
        
        return redirect('editor_contrato_unico')
    
    return render(request, 'gestao/admin/editor_contrato_unico.html', {
        'contrato': contrato,
        'site_title': 'Editor de Contrato',
        'site_header': 'ERP Imigração',
        'has_permission': True,
    })

# Manter as APIs antigas para compatibilidade (agora simplificadas)
@login_required
def gerenciar_contratos_view(request):
    """Redireciona para o novo editor único."""
    return redirect('editor_contrato_unico')

@login_required
def api_get_contrato(request):
    """
    API para buscar contrato de um tipo de visto específico.
    """
    from .models_contracts import ModeloContrato
    
    visto_id = request.GET.get('visto_id')
    
    if not visto_id:
        return JsonResponse({'exists': False})
    
    contrato = ModeloContrato.objects.filter(tipo_visto_id=visto_id, ativo=True).first()
    
    if contrato:
        return JsonResponse({
            'exists': True,
            'id': contrato.id,
            'nome': contrato.nome,
            'conteudo': contrato.conteudo,
            'ativo': contrato.ativo
        })
    else:
        return JsonResponse({'exists': False})

@login_required
def api_salvar_contrato(request):
    """
    API para salvar/atualizar contrato.
    """
    from .models_contracts import ModeloContrato
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    try:
        tipo_visto_id = request.POST.get('tipo_visto_id')
        contrato_id = request.POST.get('contrato_id')
        nome = request.POST.get('nome')
        conteudo = request.POST.get('conteudo')
        ativo = request.POST.get('ativo') == 'on'
        
        if contrato_id:
            # Atualizar existente
            contrato = ModeloContrato.objects.get(id=contrato_id)
            contrato.nome = nome
            contrato.conteudo = conteudo
            contrato.ativo = ativo
            contrato.save()
        else:
            # Criar novo
            contrato = ModeloContrato.objects.create(
                nome=nome,
                tipo_visto_id=tipo_visto_id,
                conteudo=conteudo,
                ativo=ativo
            )
        
        return JsonResponse({'success': True, 'id': contrato.id})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@user_passes_test(lambda u: u.is_superuser)
def backup_sistema_view(request):
    return render(request, 'gestao/admin/backup_sistema.html')

@user_passes_test(lambda u: u.is_superuser)
def executar_backup_view(request):
    if request.method != 'POST':
        return redirect('backup_sistema')
        
    tipo = request.POST.get('tipo', 'dados')
    base_dir = settings.BASE_DIR
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_pass = db_config['PASSWORD']
    db_host = db_config.get('HOST', '127.0.0.1')
    
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    if tipo == 'dados':
        # Backup do Banco de Dados
        try:
            env = os.environ.copy()
            if db_pass:
                env['MYSQL_PWD'] = db_pass
            
            # Tentar várias formas de encontrar mysqldump
            dump_cmd = 'mysqldump'
            
            # No Windows com XAMPP, às vezes precisamos do caminho completo
            possiveis_caminhos = [
                'mysqldump',
                r'C:\xampp\mysql\bin\mysqldump.exe',
                r'D:\xampp\mysql\bin\mysqldump.exe',
            ]
            
            result = None
            for cmd in possiveis_caminhos:
                try:
                    result = subprocess.run(
                        [cmd, '-u', db_user, '-h', db_host, db_name],
                        capture_output=True, env=env
                    )
                    if result.returncode == 0:
                        dump_cmd = cmd
                        break
                except:
                    continue
            
            if result and result.returncode == 0:
                filename = f"backup_dados_{timestamp}.sql"
                response = HttpResponse(result.stdout, content_type='application/sql')
            else:
                # Fallback: Usar dumpdata do Django se mysqldump falhar
                from django.core import management
                output = io.StringIO()
                management.call_command('dumpdata', indent=2, stdout=output)
                filename = f"backup_dados_{timestamp}.json"
                response = HttpResponse(output.getvalue(), content_type='application/json')
                
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            messages.error(request, f"Erro ao gerar backup de dados: {str(e)}")
            return redirect('backup_sistema')

    elif tipo in ['fontes', 'total']:
        # Backup de Arquivos (Zip)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Excluir pastas desnecessárias
            excluir = ['venv', '.git', '__pycache__', 'staticfiles', 'node_modules', '.agent', '.brain']
            if tipo == 'fontes':
                excluir.append('media')
                
            for root, dirs, files in os.walk(base_dir):
                dirs[:] = [d for d in dirs if d not in excluir]
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir)
                    zip_file.write(file_path, arcname)
            
            # Se for total, adicionar também o dump do banco dentro do zip
            if tipo == 'total':
                try:
                    from django.core import management
                    output = io.StringIO()
                    management.call_command('dumpdata', stdout=output)
                    zip_file.writestr(f"database_dump_{timestamp}.json", output.getvalue())
                except:
                    pass
        
        buffer.seek(0)
        filename = f"backup_{tipo}_{timestamp}.zip"
        return FileResponse(buffer, as_attachment=True, filename=filename)

    return redirect('backup_sistema')

@login_required
def estornar_fatura_view(request, doc_entry):
    """
    View para gatilhar o estorno da fatura via botão no admin.
    """
    from .services import FinanceiroService
    sucesso, msg = FinanceiroService.estornar_fatura(doc_entry)
    if sucesso:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    
    # Redireciona de volta para a lista de faturas do admin
    return redirect('admin:gestao_fatura_changelist')
