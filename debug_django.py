
import sys
import os
import django
from django.conf import settings
import pymysql

print(f"Python Executable: {sys.executable}")
print(f"Django Version: {django.get_version()}")
print(f"PyMySQL Version: {pymysql.__version__}")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
try:
    django.setup()
    print("Django Setup: SUCCESS")
except Exception as e:
    print(f"Django Setup FAILED: {e}")

# Test DB Connection via Django
from django.db import connections
from django.db.utils import OperationalError
db_conn = connections['default']
try:
    print("Testing Django DB Connection...")
    db_conn.cursor()
    print("Django DB Connection: SUCCESS")
except OperationalError as e:
    print(f"Django DB Connection FAILED: {e}")
except Exception as e:
    print(f"Django DB Connection ERROR: {e}")
