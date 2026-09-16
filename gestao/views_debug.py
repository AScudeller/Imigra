
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

def debug_clear_sessions(request):
    try:
        # Clear all sessions
        Session.objects.all().delete()
        msg = "<h1>Sessions Cleared Successfully!</h1>"
        
        # Check users
        User = get_user_model()
        user_count = User.objects.count()
        msg += f"<p>Users in DB: {user_count}</p>"
        for u in User.objects.filter(is_superuser=True):
             msg += f"<p>Superuser found: <b>{u.username}</b> (Email: {u.email})</p>"
             
        msg += "<p>Now try to <a href='/admin/'>Login to Admin</a> again.</p>"
        return HttpResponse(msg)
    except Exception as e:
        return HttpResponse(f"<h1>Error</h1><p>{e}</p>")
