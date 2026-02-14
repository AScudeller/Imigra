import pymysql
import sys
import time

SERVER_IP = '192.168.86.250'
DB_USER = 'root'
DB_PASS = ''

def test_connection():
    print(f"--- TESTANDO CONEXÃO COM O SERVIDOR {SERVER_IP} ---")
    print("Tentando conectar na porta 3306 (MySQL)...")
    
    try:
        conn = pymysql.connect(
            host=SERVER_IP,
            user=DB_USER,
            password=DB_PASS,
            connect_timeout=5
        )
        print("✅ SUCESSO! Conexão estabelecida com o banco de dados!")
        print(f"   Versão do Servidor: {conn.get_server_info()}")
        conn.close()
        return True
    except pymysql.err.OperationalError as e:
        code, msg = e.args
        print(f"❌ FALHA DE CONEXÃO: {msg}")
        
        if code == 2003:
            print("\n⚠️  DICA: Erro 2003 geralmente é FIREWALL ou MYSQL NÃO RODANDO.")
            print("   1. Verifique se o MySQL está rodando no servidor.")
            print("   2. Verifique se o Firewall do Windows no servidor liberou a porta 3306.")
        elif code == 1130:
            print("\n⚠️  DICA: Erro 1130 significa que o IP não tem permissão.")
            print("   Você rodou o arquivo 'LIBERAR_ACESSO_REMOTO.bat' lá no servidor?")
        
        return False
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n tudo pronto! Você pode rodar o sistema agora.")
    else:
        print("\n Corrija o erro acima antes de tentar rodar o sistema.")
    
    print("\nPressione ENTER para sair...")
    input()
