import json
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    user = authenticate(
        username=data.get("username"),
        password=data.get("password")
    )

    if not user:
        return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=401)

    login(request, user)

    return JsonResponse({
        "status": "success",
        "user": {
            "username": user.username,
            "role": user.role
        }
    })
