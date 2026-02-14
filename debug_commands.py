
import os
import sys
import django
from django.core.management import get_commands

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')

print("--- INICIANDO VERIFICACAO DE COMANDOS ---")
try:
    django.setup()
    print("Django setup: OK")
except Exception as e:
    print(f"ERRO no setup do Django: {e}")
    sys.exit(1)

try:
    commands = get_commands()
    print(f"\nTotal de comandos encontrados: {len(commands)}")
    print("Lista de comandos disponiveis:")
    for name, app in commands.items():
        print(f" - {name} (via {app})")
        
    if 'runserver' in commands:
        print("\n[SUCESSO] O comando 'runserver' ESTA DISPONIVEL!")
    else:
        print("\n[FALHA] O comando 'runserver' sumiu! Isso indica problema no 'django.contrib.staticfiles' ou falha de importacao.")
        
except Exception as e:
    print(f"ERRO ao listar comandos: {e}")

print("\n--- Apps Instalados (VERIFICANDO) ---")
from django.conf import settings
for app in settings.INSTALLED_APPS:
    print(f" - {app}")
