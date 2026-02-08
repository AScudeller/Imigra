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
from django.urls import path, include
from gestao.views import dashboard, cliente_portal, cliente_login
from gestao.reports import gerar_invoice_pdf, gerar_contrato_pdf
from gestao.reports_orcamento import gerar_orcamento_pdf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('portal/', cliente_portal, name='cliente_portal'),
    path('login/', cliente_login, name='cliente_login'),
    path('fatura/pdf/<int:doc_entry>/', gerar_invoice_pdf, name='gerar_invoice_pdf'),
    path('processo/contrato/<int:processo_id>/', gerar_contrato_pdf, name='gerar_contrato_pdf'),
    path('orcamento/pdf/<int:orcamento_id>/', gerar_orcamento_pdf, name='gerar_orcamento_pdf'),
    path('i18n/', include('django.conf.urls.i18n')),
]
