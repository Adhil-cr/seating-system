from django.shortcuts import render

# Create your views here.

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import admin_required
from .models import Exam
from students.models import Subject

@admin_required
def list_exams(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    exams = list(Exam.objects.values("id", "name"))
    return JsonResponse(exams, safe=False)

@csrf_exempt
@admin_required
def create_exam(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    exam = Exam.objects.create(
        name=data.get("name"),
        date=data.get("date")
    )

    subject_codes = data.get("subjects", [])

    for code in subject_codes:
        subject, _ = Subject.objects.get_or_create(code=code)
        exam.subjects.add(subject)

    return JsonResponse({"status": "exam created"})
