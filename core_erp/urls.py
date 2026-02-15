"""
URL configuration for core_erp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from gestao.views import (dashboard, cliente_portal, cliente_login, baixa_pagamento_view, 
                          api_parcelas_cliente, relatorio_inadimplencia_view,
                          editor_contrato_unico_view, backup_sistema_view, executar_backup_view,
                          estornar_fatura_view)
from gestao.reports import gerar_invoice_pdf, gerar_contrato_pdf
from gestao.reports_orcamento import gerar_orcamento_pdf

# Personalização do Admin
admin.site.site_header = "G IMIGRA - Gestão Imigratória"
admin.site.site_title = "G IMIGRA Portal"
admin.site.index_title = "Painel Administrativo"

urlpatterns = [
    path('admin/gestao/pagamento/novo-recebimento/', baixa_pagamento_view, name='baixa_pagamento'),
    path('admin/gestao/fatura/estornar/<int:doc_entry>/', estornar_fatura_view, name='estornar_fatura'),
    path('admin/gestao/api/parcelas-cliente/', api_parcelas_cliente, name='api_parcelas_cliente'),
    path('admin/gestao/relatorios/inadimplencia/', relatorio_inadimplencia_view, name='relatorio_inadimplencia'),
    path('admin/gestao/contrato-padrao/', editor_contrato_unico_view, name='editor_contrato_unico'),
    path('admin/gestao/backup/', backup_sistema_view, name='backup_sistema'),
    path('admin/gestao/backup/executar/', executar_backup_view, name='executar_backup'),
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('portal/', cliente_portal, name='cliente_portal'),
    path('login/', cliente_login, name='cliente_login'),
    path('fatura/pdf/<int:doc_entry>/', gerar_invoice_pdf, name='gerar_invoice_pdf'),
    path('processo/contrato/<int:processo_id>/', gerar_contrato_pdf, name='gerar_contrato_pdf'),
    path('orcamento/pdf/<int:orcamento_id>/', gerar_orcamento_pdf, name='gerar_orcamento_pdf'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('manual-usuario/', lambda request: render(request, 'admin/app_manual.html'), name='manual_usuario'),
]
