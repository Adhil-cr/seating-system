from django.shortcuts import render

# Create your views here.

import json
from json import JSONDecodeError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import admin_required
from .models import Hall

@csrf_exempt
@admin_required
def create_hall(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    name = (data.get("name") or "").strip()
    rows = data.get("rows")
    columns = data.get("columns")
    seats_per_bench = data.get("seats_per_bench")

    if not name or rows is None or columns is None or seats_per_bench is None:
        return JsonResponse({"error": "name, rows, columns, seats_per_bench required"}, status=400)

    try:
        rows = int(rows)
        columns = int(columns)
        seats_per_bench = int(seats_per_bench)
    except (TypeError, ValueError):
        return JsonResponse({"error": "rows, columns, seats_per_bench must be integers"}, status=400)

    if rows <= 0 or columns <= 0 or seats_per_bench <= 0:
        return JsonResponse({"error": "rows, columns, seats_per_bench must be positive"}, status=400)

    hall = Hall.objects.create(
        name=name,
        rows=rows,
        columns=columns,
        seats_per_bench=seats_per_bench,
    )

    return JsonResponse({
        "status": "hall created",
        "capacity": hall.capacity
    })
