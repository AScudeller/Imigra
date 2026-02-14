import urllib.request
import urllib.error
import time

urls = [
    ("Django (ERP)", "http://localhost:8000/admin/login/"),
    ("PHP (IAMoveis)", "http://localhost:8090/")
]

print("--- Verificando Servidores Locais ---")
print("Aguardando 2 segundos para garantir que os servidores iniciaram...")
time.sleep(2)

for name, url in urls:
    try:
        print(f"Tentando conectar em {name} ({url})...")
        with urllib.request.urlopen(url, timeout=3) as response:
            print(f"✅ {name}: ONLINE! (Status {response.status})")
    except urllib.error.URLError as e:
        print(f"❌ {name}: OFF-LINE ou Erro ({e})")
        print("   -> Voce executou o arquivo 'RUN_LOCAL_APP.bat'?")
    except Exception as e:
        print(f"❌ {name}: ERRO ({e})")
