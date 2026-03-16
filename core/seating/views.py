from django.http import JsonResponse, HttpResponse
from accounts.decorators import admin_required
from students.models import Student
from halls.models import Hall
from exams.models import Exam
from .models import SeatingAllocation, Seat
from .allocator_service import run_full_allocation_pipeline
import pandas as pd
from django.db import transaction

import json
from io import BytesIO
from json import JSONDecodeError

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
    total_students = Student.objects.filter(user=request.user).count()
    halls = Hall.objects.filter(user=request.user)

    total_capacity = sum(hall.capacity for hall in halls)

    return JsonResponse({
        "students": total_students,
        "capacity": total_capacity,
        "can_generate": total_capacity >= total_students
    })


# -------------------------
# GENERATE SEATING
# -------------------------

@admin_required
@transaction.atomic
def generate_seating(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    exam_id = data.get("exam_id")
    selected_halls = data.get("selected_halls", [])

    if not exam_id:
        return JsonResponse({"error": "exam_id required"}, status=400)

    exam = Exam.objects.filter(id=exam_id, user=request.user).first()
    if not exam:
        return JsonResponse({"error": "Exam not found"}, status=404)

    # Prevent duplicate generation (ignore stale allocations with zero seats)
    existing_allocation = SeatingAllocation.objects.filter(exam=exam).order_by("-id").first()
    if existing_allocation:
        if Seat.objects.filter(allocation=existing_allocation).exists():
            return JsonResponse({"error": "Seating already generated for this exam"}, status=400)
        # Stale allocation from a failed run – clean it up
        existing_allocation.delete()

    if selected_halls:
        halls_qs = Hall.objects.filter(id__in=selected_halls, user=request.user)
    else:
        halls_qs = Hall.objects.filter(user=request.user)

    halls = list(halls_qs)
    if not halls:
        return JsonResponse({"error": "No halls selected"}, status=400)

    subject_codes = list(getattr(exam, "subject_codes", []) or [])
    if not subject_codes:
        subject_codes = list(exam.subjects.values_list("code", flat=True))
    subject_codes = [str(code).strip().replace(".0", "") for code in subject_codes if str(code).strip()]

    total_students = Student.objects.filter(
        user=request.user,
        subjects__code__in=subject_codes
    ).distinct().count()
    total_capacity = sum(h.capacity for h in halls)

    if total_capacity < total_students:
        return JsonResponse({"error": "Not enough seats available"}, status=400)

    # -----------------------------
    # STEP 1: Run full algorithm pipeline
    # -----------------------------
    try:
        csv_output = run_full_allocation_pipeline(exam, halls=halls_qs)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception:
        return JsonResponse({"error": "Seating generation failed"}, status=500)

    # -----------------------------
    # STEP 2: Read algorithm output
    # -----------------------------
    df = pd.read_csv(csv_output)

    halls = list(halls_qs)

    if df.empty:
        return JsonResponse({"error": "Seating generation produced no rows"}, status=400)

    # Create allocation record (only after we know we have data)
    allocation = SeatingAllocation.objects.create(exam=exam)

    # -----------------------------
    # STEP 3: Convert to Django seats
    # -----------------------------
    for _, row in df.iterrows():

        hall_index = int(row["hall_id"]) - 1
        hall = halls[hall_index]

        seat_number = int(row["seat_number"])

        column_count = hall.columns

        row_no = (seat_number - 1) // column_count + 1
        column_no = (seat_number - 1) % column_count + 1

        student = Student.objects.filter(
            user=request.user,
            register_no=row["register_no"]
        ).first()

        if not student:
            raise ValueError(f"Student not found: {row['register_no']}")

        Seat.objects.create(
            allocation=allocation,
            hall=hall,
            row=row_no,
            column=column_no,
            student=student
        )

    return JsonResponse({"status": "seating generated using algorithm"})

# -------------------------
# VIEW SEATING
# -------------------------

@admin_required
def view_seating(request):

    exam_id = request.GET.get("exam_id")

    if not exam_id:
        return JsonResponse({"error": "exam_id required"}, status=400)

    allocation = SeatingAllocation.objects.filter(
        exam_id=exam_id,
        exam__user=request.user
    ).last()

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
        seats = seats.filter(student__subjects__code=subject_filter)

    seats = seats.distinct()

    # FIX: deduplicate seats for multi-subject students
    seen_registers = set()
    unique_seats = []
    for seat in seats:
        reg_no = seat.student.register_no
        if reg_no in seen_registers:
            continue
        seen_registers.add(reg_no)
        unique_seats.append(seat)

    seats = unique_seats

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

    allocation = SeatingAllocation.objects.filter(
        exam_id=exam_id,
        exam__user=request.user
    ).last()

    if not allocation:
        return JsonResponse({"error": "No seating generated"}, status=404)

    exam = Exam.objects.filter(id=exam_id, user=request.user).first()
    if not exam:
        return JsonResponse({"error": "Exam not found"}, status=404)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Exam: {exam.name}", styles["Heading1"]))
    elements.append(Paragraph(f"Date: {exam.date}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    seats = (
        Seat.objects.filter(allocation=allocation)
        .select_related("hall", "student")
        .order_by("hall__name", "row", "column")
    )

    # FIX: deduplicate seats for multi-subject students
    seen_registers = set()
    unique_seats = []
    for seat in seats:
        reg_no = seat.student.register_no
        if reg_no in seen_registers:
            continue
        seen_registers.add(reg_no)
        unique_seats.append(seat)
    seats = unique_seats

    # Group seats by hall for hall-wise tables
    halls = {}
    for seat in seats:
        halls.setdefault(seat.hall_id, {
            "hall": seat.hall,
            "seats": []
        })
        halls[seat.hall_id]["seats"].append(seat)

    for hall_id, hall_data in halls.items():
        hall = hall_data["hall"]
        hall_seats = hall_data["seats"]

        elements.append(Paragraph(f"Hall: {hall.name}", styles["Heading2"]))
        elements.append(Spacer(1, 6))

        data = [["Seat No", "Row", "Column", "Register No", "Name", "Department"]]

        for seat in hall_seats:
            seat_no = (seat.row - 1) * hall.columns + seat.column
            data.append([
                seat_no,
                seat.row,
                seat.column,
                seat.student.register_no,
                seat.student.name,
                seat.student.department
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

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

    allocation = SeatingAllocation.objects.filter(
        exam_id=exam_id,
        exam__user=request.user
    ).last()

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
