
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session
from django.db import connection

print("--- DEBUGGING LOGIN PROCESS ---")

# 1. Clear Sessions
print("1. Clearing all sessions...")
try:
    Session.objects.all().delete()
    print("   Sessions cleared successfully.")
except Exception as e:
    print(f"   Error clearing sessions: {e}")

# 2. Check Database Connection
print("\n2. Checking Database Users...")
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    count = User.objects.count()
    print(f"   User count: {count}")
    for u in User.objects.all():
        print(f"   - User: {u.username} (Email: {u.email}) | Active: {u.is_active} | Staff: {u.is_staff} | Superuser: {u.is_superuser}")
except Exception as e:
    print(f"   Error querying users: {e}")

# 3. Test Authentication
print("\n3. Testing Authentication manually...")
username = 'admin'  # Default guess
password = 'admin123' # Default guess
print(f"   Attempting login for '{username}' with password '{password}'...")
try:
    user = authenticate(username=username, password=password)
    if user:
        print(f"   SUCCESS: Authenticated as {user}")
    else:
        print("   FAILED: Authentication returned None")
except Exception as e:
    print(f"   EXCEPTION during authenticate(): {e}")
    import traceback
    traceback.print_exc()

print("\n--- DEBUG COMPLETE ---")
