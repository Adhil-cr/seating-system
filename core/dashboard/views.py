from django.http import JsonResponse
from accounts.decorators import admin_required
from students.models import Student
from halls.models import Hall
from exams.models import Exam
from seating.models import SeatingAllocation

@admin_required
def dashboard_summary(request):
    total_students = Student.objects.filter(user=request.user).count()
    halls_qs = Hall.objects.filter(user=request.user, is_active=True)
    total_halls = halls_qs.count()
    total_exams = Exam.objects.filter(user=request.user).count()
    allocated_exam_ids = SeatingAllocation.objects.filter(
        exam__user=request.user
    ).values_list("exam_id", flat=True).distinct()
    pending_allocations = max(total_exams - allocated_exam_ids.count(), 0)

    last_allocation = SeatingAllocation.objects.filter(
        exam__user=request.user
    ).select_related("exam").order_by("-created_at").first()
    last_status = "Generated" if last_allocation else "Not Generated"
    last_status_class = "success" if last_allocation else "warning"

    total_capacity = sum(h.capacity for h in halls_qs)

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
    if total_exams == 0:
        alerts.append({
            "level": "warning",
            "message": "No exams created yet."
        })
    if pending_allocations > 0:
        alerts.append({
            "level": "warning",
            "message": f"{pending_allocations} exam(s) pending seating allocation."
        })
    if total_students > 0 and total_halls > 0 and total_capacity < total_students:
        alerts.append({
            "level": "warning",
            "message": "Hall capacity is less than total students."
        })
    if not alerts:
        alerts.append({
            "level": "success",
            "message": "All systems look good."
        })

    halls = []
    for hall in halls_qs.order_by("name"):
        halls.append({
            "id": hall.id,
            "name": hall.name,
            "rows": hall.rows,
            "columns": hall.columns,
            "seats_per_bench": hall.seats_per_bench,
            "capacity": hall.capacity,
        })

    return JsonResponse({
        "status": "ok",
        "total_students": total_students,
        "total_halls": total_halls,
        "total_exams": total_exams,
        "pending_allocations": pending_allocations,
        "last_status": last_status,
        "last_status_class": last_status_class,
        "total_capacity": total_capacity,
        "alerts": alerts,
        "halls": halls,
    })
