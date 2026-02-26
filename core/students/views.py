from django.shortcuts import render

# Create your views here.

import csv, io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student

@csrf_exempt
def upload_students(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file"}, status=400)

    decoded = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    invalid = []
    success = 0

    for i, row in enumerate(reader, start=2):
        reg = row.get("register_no")
        name = row.get("name")
        dept = row.get("department")

        if not reg or not name or not dept:
            invalid.append({"row": i, "error": "Missing fields"})
            continue

        if Student.objects.filter(register_no=reg).exists():
            invalid.append({"row": i, "error": "Duplicate register number"})
            continue

        Student.objects.create(
            register_no=reg,
            name=name,
            department=dept
        )
        success += 1

    return JsonResponse({
        "uploaded": success,
        "invalid_rows": invalid
    })