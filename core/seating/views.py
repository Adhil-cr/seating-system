from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import admin_required
from students.models import Student
from halls.models import Hall
from exams.models import Exam
from .models import SeatingAllocation, Seat
from .allocator import simple_allocator

import json
from io import BytesIO

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Excel
from openpyxl import Workbook


# -------------------------
# PREVIEW SEATING
# -------------------------

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


# -------------------------
# GENERATE SEATING
# -------------------------

@csrf_exempt
@admin_required
def generate_seating(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    exam_id = data.get("exam_id")

    if not exam_id:
        return JsonResponse({"error": "exam_id required"}, status=400)

    exam = Exam.objects.get(id=exam_id)

    # Prevent duplicate generation
    if SeatingAllocation.objects.filter(exam=exam).exists():
        return JsonResponse({"error": "Seating already generated for this exam"}, status=400)

    total_students = Student.objects.count()
    total_capacity = sum(h.capacity for h in Hall.objects.all())

    if total_capacity < total_students:
        return JsonResponse({"error": "Not enough seats available"}, status=400)

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


# -------------------------
# VIEW SEATING
# -------------------------

@admin_required
def view_seating(request):

    exam_id = request.GET.get("exam_id")

    if not exam_id:
        return JsonResponse({"error": "exam_id required"}, status=400)

    allocation = SeatingAllocation.objects.filter(exam_id=exam_id).last()

    if not allocation:
        return JsonResponse({"error": "No seating generated"}, status=404)

    seats = Seat.objects.filter(allocation=allocation).select_related("hall", "student")

    # Department filter
    department_filter = request.GET.get("department")
    if department_filter:
        seats = seats.filter(student__department=department_filter)

    # Subject filter
    subject_filter = request.GET.get("subject")
    if subject_filter:
        seats = seats.filter(allocation__exam__subjects__code=subject_filter)

    halls_data = {}

    for seat in seats:

        hall_name = seat.hall.name

        if hall_name not in halls_data:
            halls_data[hall_name] = {
                "rows": seat.hall.rows,
                "columns": seat.hall.columns,
                "seats": []
            }

        halls_data[hall_name]["seats"].append({
            "row": seat.row,
            "column": seat.column,
            "register_no": seat.student.register_no,
            "name": seat.student.name,
            "department": seat.student.department
        })

    return JsonResponse({
        "exam_id": exam_id,
        "halls": halls_data
    })


# -------------------------
# EXPORT PDF
# -------------------------

@admin_required
def export_pdf(request):

    exam_id = request.GET.get("exam_id")

    if not exam_id:
        return JsonResponse({"error": "exam_id required"}, status=400)

    allocation = SeatingAllocation.objects.filter(exam_id=exam_id).last()

    if not allocation:
        return JsonResponse({"error": "No seating generated"}, status=404)

    exam = Exam.objects.get(id=exam_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Exam: {exam.name}", styles["Heading1"]))
    elements.append(Paragraph(f"Date: {exam.date}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    seats = Seat.objects.filter(allocation=allocation).select_related("hall", "student")

    data = [["Hall", "Row", "Column", "Register No", "Name"]]

    for seat in seats:
        data.append([
            seat.hall.name,
            seat.row,
            seat.column,
            seat.student.register_no,
            seat.student.name
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return HttpResponse(buffer, content_type="application/pdf")


# -------------------------
# EXPORT EXCEL
# -------------------------

@admin_required
def export_excel(request):

    exam_id = request.GET.get("exam_id")

    if not exam_id:
        return JsonResponse({"error": "exam_id required"}, status=400)

    allocation = SeatingAllocation.objects.filter(exam_id=exam_id).last()

    if not allocation:
        return JsonResponse({"error": "No seating generated"}, status=404)

    wb = Workbook()
    ws = wb.active
    ws.title = "Seating"

    ws.append(["Hall", "Row", "Column", "Register No", "Name", "Department"])

    seats = Seat.objects.filter(allocation=allocation).select_related("hall", "student")

    for seat in seats:
        ws.append([
            seat.hall.name,
            seat.row,
            seat.column,
            seat.student.register_no,
            seat.student.name,
            seat.student.department
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = "attachment; filename=seating.xlsx"

    wb.save(response)

    return response