from django.http import JsonResponse
from accounts.decorators import admin_required
from students.models import Student
from halls.models import Hall

from django.views.decorators.csrf import csrf_exempt
from .models import SeatingAllocation, Seat
from exams.models import Exam
from .allocator import simple_allocator
import json


@admin_required
def preview_seating(request):
    total_students = Student.objects.count()
    halls = Hall.objects.all()

    total_capacity = sum(hall.capacity for hall in halls)

    return JsonResponse({
        "students": total_students,
        "capacity": total_capacity,
        "can_generate": total_capacity >= total_students
    })





@csrf_exempt
@admin_required
def generate_seating(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    exam_id = data.get("exam_id")

    exam = Exam.objects.get(id=exam_id)

    allocation = SeatingAllocation.objects.create(exam=exam)

    seat_map = simple_allocator()

    for seat_data in seat_map:
        Seat.objects.create(
            allocation=allocation,
            hall=seat_data["hall"],
            row=seat_data["row"],
            column=seat_data["column"],
            student=seat_data["student"]
        )

    return JsonResponse({"status": "seating generated"})