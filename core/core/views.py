from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model

def login_page(request):
    return render(request, "auth/login.html")

def signup_page(request):
    if request.method == "GET":
        return render(request, "auth/signup.html")

    full_name = request.POST.get("full_name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    password_confirm = request.POST.get("password_confirm", "")

    if not full_name or not email or not password or not password_confirm:
        return render(request, "auth/signup.html", {
            "error": "All fields are required."
        })

    if password != password_confirm:
        return render(request, "auth/signup.html", {
            "error": "Passwords do not match."
        })

    User = get_user_model()
    if User.objects.filter(username=email).exists():
        return render(request, "auth/signup.html", {
            "error": "An account with this email already exists."
        })

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )
    user.first_name = full_name
    user.save(update_fields=["first_name"])

    login(request, user)
    return redirect("dashboard")

def dashboard_page(request):
    return render(request, "dashboard/dashboard.html")

def upload_students_page(request):
    return render(request, "students/upload.html")

def exam_config_page(request):
    return render(request, "exams/config.html")

def seating_generate_page(request):
    return render(request, "seating/generate.html")

def seating_view_page(request):
    return render(request, "seating/view.html")

def profile_page(request):
    return render(request, "profile/profile.html")
