from django.shortcuts import render

# Create your views here.

import json
from json import JSONDecodeError
from datetime import datetime
from django.http import JsonResponse
from django.db.utils import OperationalError, ProgrammingError
from accounts.decorators import admin_required
from dashboard.models import ActivityLog
from .models import Exam
from students.models import Subject, Student


def _normalize_subject_codes(raw_codes):
    if raw_codes is None:
        return []
    if isinstance(raw_codes, str):
        raw_codes = [s.strip() for s in raw_codes.split(",")]
    elif not isinstance(raw_codes, (list, tuple, set)):
        return []

    codes = []
    for code in raw_codes:
        code_str = str(code).strip().replace(".0", "")
        if code_str:
            codes.append(code_str)

    seen = set()
    unique_codes = []
    for code in codes:
        if code not in seen:
            unique_codes.append(code)
            seen.add(code)
    return unique_codes


@admin_required
def list_exams(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    exams_data = []
    try:
        exams = Exam.objects.filter(user=request.user).prefetch_related("subjects")
        for exam in exams:
            subject_codes = _normalize_subject_codes(
                getattr(exam, "subject_codes", None)
            )
            if not subject_codes:
                subject_codes = list(exam.subjects.values_list("code", flat=True))

            if subject_codes:
                student_count = Student.objects.filter(
                    user=request.user,
                    subjects__code__in=subject_codes
                ).values("register_no").distinct().count()
            else:
                student_count = 0

            exams_data.append({
                "id": exam.id,
                "name": exam.name,
                "session": exam.session,
                "student_count": student_count
            })
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {"error": "Database schema is out of date. Run migrations."},
            status=500
        )

    return JsonResponse(exams_data, safe=False)


@admin_required
def create_exam(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    name = (data.get("name") or "").strip()
    date_str = data.get("date")
    session = (data.get("session") or "").strip().upper()

    raw_subjects = data.get("subject_codes")
    if raw_subjects in (None, ""):
        raw_subjects = data.get("subjects", "")
    subject_codes = _normalize_subject_codes(raw_subjects)

    if not name or not date_str or not session:
        return JsonResponse({"error": "name, date, and session required"}, status=400)

    if session not in [Exam.SESSION_AM, Exam.SESSION_PM]:
        return JsonResponse({"error": "Invalid session value"}, status=400)

    if not subject_codes:
        return JsonResponse({"error": "subject_codes required"}, status=400)

    try:
        exam_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    try:
        exam = Exam.objects.create(
            user=request.user,
            name=name,
            date=exam_date,
            session=session,
            subject_codes=subject_codes
        )

        for code in subject_codes:
            subject, _ = Subject.objects.get_or_create(code=code)
            exam.subjects.add(subject)
    except (OperationalError, ProgrammingError):
        return JsonResponse(
            {"error": "Database schema is out of date. Run migrations."},
            status=500
        )

    student_count = Student.objects.filter(
        user=request.user,
        subjects__code__in=subject_codes
    ).values("register_no").distinct().count()

    try:
        ActivityLog.objects.create(
            user=request.user,
            action=f"Created exam: {exam.name}"
        )
    except (OperationalError, ProgrammingError):
        pass

    return JsonResponse({
        "message": "Exam created successfully",
        "student_count": student_count,
        "total_students": student_count
    })
