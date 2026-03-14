from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from students.models import Student
from halls.models import Hall
from exams.models import Exam
from seating.models import SeatingAllocation


@ensure_csrf_cookie
def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
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


@login_required
def dashboard_page(request):
    total_students = Student.objects.filter(user=request.user).count()
    total_halls = Hall.objects.filter(user=request.user).count()
    total_exams = Exam.objects.filter(user=request.user).count()
    allocated_exam_ids = SeatingAllocation.objects.filter(
        exam__user=request.user
    ).values_list("exam_id", flat=True).distinct()
    pending_allocations = max(total_exams - allocated_exam_ids.count(), 0)

    last_allocation = SeatingAllocation.objects.filter(
        exam__user=request.user
    ).select_related("exam").order_by(
        "-created_at"
    ).first()
    last_status = "Generated" if last_allocation else "Not Generated"
    last_status_class = "success" if last_allocation else "warning"

    total_capacity = sum(
        h.capacity for h in Hall.objects.filter(user=request.user)
    )
    alerts = []
    if total_students == 0:
        alerts.append({
            "level": "warning",
            "message": "No students uploaded yet."
        })
    if total_halls == 0:
        alerts.append({
            "level": "warning",
            "message": "No halls configured yet."
        })
    if total_students > 0 and total_halls > 0 and total_capacity < total_students:
        alerts.append({
            "level": "warning",
            "message": "Hall capacity is less than total students."
        })

    context = {
        "total_students": total_students,
        "total_halls": total_halls,
        "pending_allocations": pending_allocations,
        "last_status": last_status,
        "last_status_class": last_status_class,
        "alerts": alerts
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
@ensure_csrf_cookie
def upload_students_page(request):
    return render(request, "students/upload.html")


@login_required
@ensure_csrf_cookie
def exam_config_page(request):
    return render(request, "exams/config.html")


@login_required
@ensure_csrf_cookie
def seating_generate_page(request):
    return render(request, "seating/generate.html")


@login_required
def seating_view_page(request):
    return render(request, "seating/view.html")


@login_required
def profile_page(request):
    context = {
        "total_students": Student.objects.filter(user=request.user).count(),
        "total_halls": Hall.objects.filter(user=request.user).count(),
        "total_allocations": SeatingAllocation.objects.filter(
            exam__user=request.user
        ).count()
    }
    return render(request, "profile/profile.html", context)
