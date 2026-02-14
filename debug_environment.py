
import os
import sys
import traceback

print("--- INICIANDO DIAGNOSTICO DE AMBIENTE ---")
print(f"Python: {sys.version}")
print(f"Executavel: {sys.executable}")
print(f"Caminho: {sys.path}")

try:
    import django
    print(f"Django Versao: {django.get_version()}")
except ImportError:
    print("CRITICO: Django nao esta instalado!")
    sys.exit(1)

try:
    import pymysql
    print(f"PyMySQL Versao: {pymysql.__version__}")
except ImportError:
    print("CRITICO: PyMySQL nao esta instalado!")

print("\n--- TENTANDO CARREGAR SETTINGS ---")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')

try:
    from django.conf import settings
    print(f"INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps configurados.")
except Exception:
    print("ERRO ao ler settings.py:")
    traceback.print_exc()

print("\n--- TENTANDO INICIALIZAR DJANGO ---")
try:
    django.setup()
    print("SUCESSO: Django inicializado corretamente!")
except Exception:
    print("FALHA CRITICA na inicializacao do Django:")
    traceback.print_exc()

print("\n--- DIAGNOSTICO FINALIZADO ---")
