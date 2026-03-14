import json
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect


def _get_request_data(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body or "{}")
        except JSONDecodeError:
            return None
    return request.POST


def signup_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = _get_request_data(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return JsonResponse({"error": "username and password required"}, status=400)

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password
    )

    login(request, user)

    return JsonResponse({"message": "User created and logged in"})


def login_view(request):
    if request.method == "GET":
        return JsonResponse({"error": "Login required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = _get_request_data(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return JsonResponse({"error": "username and password required"}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    login(request, user)

    return JsonResponse({"message": "Login successful"})


def logout_view(request):
    logout(request)
    if request.method == "GET":
        next_url = request.GET.get("next") or "/"
        return redirect(next_url)
    return JsonResponse({"message": "Logged out"})
