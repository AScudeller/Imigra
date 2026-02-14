
import os
import sys

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')

try:
    import django
    django.setup()
    
    from django.core.management import execute_from_command_line
    from django.urls import resolve
    from django.test import RequestFactory
    
    print("\n--- TESTANDO ROTAS ---")
    
    # 1. Testar se a URL raiz existe
    try:
        match = resolve('/')
        print(f"Rota raiz encontrada: {match.view_name}")
    except Exception as e:
        print(f"ERRO Rota raiz: {e}")
        
    # 2. Testar se admin existe
    try:
        match = resolve('/admin/login/')
        print(f"Rota admin encontrada: {match.view_name}")
    except Exception as e:
        print(f"ERRO Rota admin: {e}")

    # 3. Testar conexão com banco real
    print("\n--- TESTANDO BANCO DE DADOS (QUERY REAL) ---")
    from django.db import connections
    from django.contrib.auth.models import User
    
    try:
        count = User.objects.count()
        print(f"Sucesso! Total de Usuarios no banco: {count}")
    except Exception as e:
        print("ERRO CRITICO AO ACESSAR O BANCO:")
        print(e)
        
except Exception as global_e:
    print(f"ERRO GERAL: {global_e}")
    import traceback
    traceback.print_exc()
