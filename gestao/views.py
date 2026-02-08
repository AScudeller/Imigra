from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Cliente, Processo, Fatura, Parcela, Pagamento, TipoVisto, Lead, Documento, EtapaProcesso
from django.db.models import Sum, Count, F
from django.utils import timezone

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
