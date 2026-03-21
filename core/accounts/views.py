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

    email = (data.get("email") or data.get("email_id") or "").strip()
    username = (data.get("username") or email or "").strip()
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or ""

    if not username or not password:
        return JsonResponse({"error": "username/email and password required"}, status=400)

    if password_confirm and password != password_confirm:
        return JsonResponse({"error": "Passwords do not match"}, status=400)

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)
    if email and User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email or None
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

    identifier = (data.get("username") or data.get("email") or data.get("email_id") or "").strip()
    password = data.get("password") or ""

    if not identifier or not password:
        return JsonResponse({"error": "username/email and password required"}, status=400)

    user = None
    User = get_user_model()
    if "@" in identifier:
        matches = User.objects.filter(email__iexact=identifier)
        if matches.count() > 1:
            return JsonResponse({"error": "Multiple users with this email"}, status=400)
        if matches.exists():
            user_obj = matches.first()
            user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            user = authenticate(request, username=identifier, password=password)
    else:
        user = authenticate(request, username=identifier, password=password)

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
