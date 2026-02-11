from django.http import JsonResponse
from accounts.decorators import admin_required

@admin_required
def dashboard_summary(request):
    return JsonResponse({
        "status": "ok",
        "message": "Dashboard connected"
    })
