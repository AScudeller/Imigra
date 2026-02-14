import os
import django
import sys

# Configure Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def setup_permissions():
    print("Iniciando configuração de permissões estilo SAP B1 (G IMIGRA)...")

    # 1. Grupo FINANCEIRO
    financeiro_group, _ = Group.objects.get_or_create(name='Financeiro')
    print("- Configurando grupo: Financeiro")
    
    # Permissões do Financeiro
    perms_financeiro = [
        'view_fatura', 'add_fatura', 'change_fatura',
        'view_parcela', 'change_parcela',
        'view_pagamento', 'add_pagamento',
        'view_despesa', 'add_despesa', 'change_despesa',
        'view_cliente', # Precisa ver cliente para faturar
        'view_lognotificacao',
        'view_orcamento', 'change_orcamento', # Financeiro converte em fatura
    ]
    for p_code in perms_financeiro:
        p = Permission.objects.filter(codename=p_code).first()
        if p: financeiro_group.permissions.add(p)

    # 2. Grupo OPERACIONAL (Consultores)
    operacional_group, _ = Group.objects.get_or_create(name='Operacional')
    print("- Configurando grupo: Operacional")
    
    perms_operacional = [
        'view_cliente', 'add_cliente', 'change_cliente',
        'view_processo', 'add_processo', 'change_processo',
        'view_documento', 'add_documento', 'change_documento',
        'view_etapaprocesso', 'change_etapaprocesso',
        'view_tipovisto',
        'view_lognotificacao',
    ]
    for p_code in perms_operacional:
        p = Permission.objects.filter(codename=p_code).first()
        if p: operacional_group.permissions.add(p)

    # 3. Grupo COMERCIAL (Sales)
    comercial_group, _ = Group.objects.get_or_create(name='Comercial')
    print("- Configurando grupo: Comercial")
    
    perms_comercial = [
        'view_lead', 'add_lead', 'change_lead',
        'view_cliente', 'add_cliente',
        'view_tipovisto',
        'view_orcamento', 'add_orcamento', 'change_orcamento',
    ]
    for p_code in perms_comercial:
        p = Permission.objects.filter(codename=p_code).first()
        if p: comercial_group.permissions.add(p)

    print("\n--- CONFIGURAÇÃO DE SEGURANÇA CONCLUÍDA ---")
    print("Grupos criados: Financeiro, Operacional e Comercial.")
    print("Use o Django Admin para atribuir usuários a estes grupos.")

if __name__ == "__main__":
    setup_permissions()
