"""
Script de teste de conexão MySQL
Testa a conexão com o banco de dados antes de gerar os models
"""

import pymysql
import sys

# Configurações do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'iamoveis_calculos',
    'charset': 'utf8mb4'
}

print("=" * 60)
print("TESTE DE CONEXÃO MYSQL")
print("=" * 60)
print()

# Tentar diferentes configurações
configs_to_try = [
    {'host': 'localhost', 'port': 3306},
    {'host': '127.0.0.1', 'port': 3306},
    {'host': '::1', 'port': 3306},  # IPv6
]

for i, config in enumerate(configs_to_try, 1):
    print(f"Tentativa {i}: {config['host']}:{config['port']}")
    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        print(f"✓ SUCESSO! Conectado em {config['host']}:{config['port']}")
        
        # Testar se o banco existe
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES LIKE 'iamoveis_calculos'")
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Banco 'iamoveis_calculos' encontrado!")
            
            # Contar tabelas
            cursor.execute("USE iamoveis_calculos")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Total de tabelas: {len(tables)}")
            
            if tables:
                print("\nPrimeiras 10 tabelas:")
                for table in tables[:10]:
                    print(f"  - {table[0]}")
        else:
            print(f"✗ Banco 'iamoveis_calculos' NÃO encontrado!")
        
        cursor.close()
        connection.close()
        
        print()
        print("=" * 60)
        print(f"CONFIGURAÇÃO CORRETA: host='{config['host']}'")
        print("=" * 60)
        sys.exit(0)
        
    except Exception as e:
        print(f"✗ FALHOU: {str(e)}")
        print()

print("=" * 60)
print("ERRO: Nenhuma configuração funcionou!")
print("=" * 60)
sys.exit(1)
